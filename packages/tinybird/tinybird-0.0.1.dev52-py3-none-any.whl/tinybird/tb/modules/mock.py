import logging
import os
from pathlib import Path
from typing import Optional

import click

from tinybird.client import TinyB
from tinybird.prompts import mock_prompt
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import CLIException, check_user_token_with_client, coro
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.fixture import build_fixture_name, persist_fixture
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.llm import LLM
from tinybird.tb.modules.llm_utils import extract_xml
from tinybird.tb.modules.project import Project


@cli.command()
@click.argument("datasource", type=str)
@click.option("--rows", type=int, default=10, help="Number of events to send")
@click.option(
    "--prompt",
    type=str,
    default="",
    help="Extra context to use for data generation",
)
@click.option("--skip", is_flag=True, default=False, help="Skip following up on the generated data")
@click.pass_context
@coro
async def mock(ctx: click.Context, datasource: str, rows: int, prompt: str, skip: bool) -> None:
    """Generate sample data for a datasource.

    Args:
        datasource: Path to the datasource file to load sample data into
        rows: Number of events to send
        prompt: Extra context to use for data generation
        skip: Skip following up on the generated data
    """

    try:
        tb_client: TinyB = ctx.ensure_object(dict)["client"]
        project: Project = ctx.ensure_object(dict)["project"]
        datasource_path = Path(datasource)
        datasource_name = datasource
        folder = project.folder
        click.echo(FeedbackManager.highlight(message=f"\n» Creating fixture for {datasource_name}..."))
        if datasource_path.suffix == ".datasource":
            datasource_name = datasource_path.stem
        else:
            datasource_path = Path("datasources", f"{datasource}.datasource")
        datasource_path = Path(folder) / datasource_path

        if not datasource_path.exists():
            raise CLIException(f"Datasource '{datasource_path.stem}' not found")

        prompt_path = Path(folder) / "fixtures" / f"{datasource_name}.prompt"
        if not prompt or prompt == "Use the datasource schema to generate sample data":
            # load the prompt from the fixture.prompt file if it exists
            if prompt_path.exists():
                prompt = prompt_path.read_text()
        else:
            click.echo(FeedbackManager.info(message="* Overriding last prompt..."))
            prompt_path.write_text(prompt)

        datasource_content = datasource_path.read_text()
        config = CLIConfig.get_project_config()
        user_client = config.get_client()
        user_token = config.get_user_token()

        try:
            if not user_token:
                raise CLIException("No user token found")
            await check_user_token_with_client(user_client, token=user_token)
        except Exception:
            click.echo(FeedbackManager.error(message="This action requires authentication. Run 'tb login' first."))
            return
        llm = LLM(user_token=user_token, host=user_client.host)
        prompt = f"<datasource_schema>{datasource_content}</datasource_schema>\n<user_input>{prompt}</user_input>"
        iterations = 0
        history = ""
        fixture_path: Optional[Path] = None
        sql = ""
        while iterations < 10:
            feedback = ""
            if iterations > 0:
                feedback = click.prompt("\nFollow-up instructions or continue", default="continue")
            if iterations > 0 and (not feedback or feedback in ("continue", "ok", "exit", "quit", "q")):
                break
            else:
                if iterations > 0:
                    if fixture_path:
                        fixture_path.unlink()
                    fixture_path = None
                    click.echo(FeedbackManager.highlight(message=f"\n» Creating fixture for {datasource_name}..."))

                response = llm.ask(system_prompt=mock_prompt(rows, feedback, history), prompt=prompt)
                sql = extract_xml(response, "sql")
                result = await tb_client.query(f"{sql} FORMAT JSON")
                data = result.get("data", [])[:rows]
                fixture_name = build_fixture_name(str(datasource_path), datasource_name, datasource_content)
                fixture_path = persist_fixture(fixture_name, data, folder)
                click.echo(FeedbackManager.info(message=f"✓ /fixtures/{fixture_name}.ndjson created"))

                if os.environ.get("TB_DEBUG", "") != "":
                    logging.debug(sql)

                history = (
                    history
                    + f"""
                <result_iteration_{iterations}>
                    {response}
                </result_iteration_{iterations}>
                """
                )
                if skip:
                    break
                iterations += 1

        click.echo(FeedbackManager.success(message=f"✓ Sample data for {datasource_name} created with {rows} rows"))

    except Exception as e:
        click.echo(FeedbackManager.error_exception(error=f"Error: {e}"))
