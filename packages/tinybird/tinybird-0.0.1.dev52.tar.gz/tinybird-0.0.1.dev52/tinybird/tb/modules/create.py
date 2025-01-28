import os
import re
from os import getcwd
from pathlib import Path
from typing import Optional

import click

from tinybird.client import TinyB
from tinybird.prompts import create_prompt, mock_prompt, rules_prompt
from tinybird.tb.modules.cicd import init_cicd
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import _generate_datafile, check_user_token_with_client, coro, generate_datafile
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.fixture import build_fixture_name, persist_fixture
from tinybird.tb.modules.exceptions import CLIException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.llm import LLM
from tinybird.tb.modules.llm_utils import extract_xml, parse_xml
from tinybird.tb.modules.project import Project


@cli.command()
@click.option(
    "--data",
    type=click.Path(exists=True),
    default=None,
    help="Initial data to be used to create the project",
)
@click.option(
    "--prompt",
    type=str,
    default=None,
    help="Prompt to be used to create the project",
)
@click.option(
    "--folder",
    default="",
    type=click.Path(exists=False, file_okay=False),
    help="Folder where datafiles will be placed",
)
@click.option("--rows", type=int, default=10, help="Number of events to send")
@click.option("--source", type=str, default="tb", help="Source of the command")
@click.option("--skip", is_flag=True, default=False, help="Skip following up on the generated data")
@click.pass_context
@coro
async def create(
    ctx: click.Context,
    data: Optional[str],
    prompt: Optional[str],
    folder: Optional[str],
    rows: int,
    source: str,
    skip: bool,
) -> None:
    """Initialize a new project."""
    project: Project = ctx.ensure_object(dict)["project"]
    local_client: TinyB = ctx.ensure_object(dict)["client"]
    folder = folder or getcwd()
    folder_path = Path(folder)
    if not folder_path.exists():
        folder_path.mkdir()

    try:
        config = CLIConfig.get_project_config(str(project.path))
        tb_client = config.get_client()
        user_token: Optional[str] = None
        if prompt:
            try:
                user_token = config.get_user_token()
                if not user_token:
                    raise CLIException("No user token found")
                await check_user_token_with_client(tb_client, token=user_token)
            except Exception as e:
                click.echo(
                    FeedbackManager.error(
                        message=f"This action requires authentication. Run 'tb login' first. Error: {e}"
                    )
                )
                return

        if not validate_project_structure(folder):
            click.echo(FeedbackManager.highlight(message="\n» Creating new project structure..."))
            create_project_structure(folder)
            click.echo(FeedbackManager.success(message="✓ Scaffolding completed!\n"))

        result = ""
        if data or prompt:
            click.echo(FeedbackManager.highlight(message="\n» Creating resources..."))
            result = await create_resources(local_client, tb_client, user_token, data, prompt, folder, skip)
            click.echo(FeedbackManager.success(message="✓ Done!\n"))

        if not already_has_cicd(folder):
            click.echo(FeedbackManager.highlight(message="\n» Creating CI/CD files for GitHub and GitLab..."))
            init_git(folder)
            await init_cicd(data_project_dir=os.path.relpath(folder))
            click.echo(FeedbackManager.success(message="✓ Done!\n"))

        if not already_has_cursor_rules(folder):
            click.echo(FeedbackManager.highlight(message="\n» Creating .cursorrules..."))
            create_rules(folder, source, "cursor")
            click.echo(FeedbackManager.success(message="✓ Done!\n"))

        if should_generate_fixtures(result):
            click.echo(FeedbackManager.highlight(message="\n» Generating fixtures..."))

            if data:
                ds_name = os.path.basename(data.split(".")[0])
                data_content = Path(data).read_text()
                datasource_path = Path(folder) / "datasources" / f"{ds_name}.datasource"
                fixture_name = build_fixture_name(
                    datasource_path.absolute().as_posix(), ds_name, datasource_path.read_text()
                )
                click.echo(FeedbackManager.info(message=f"✓ /fixtures/{ds_name}"))
                persist_fixture(fixture_name, data_content, folder)
            elif prompt and user_token:
                datasource_files = [f for f in os.listdir(Path(folder) / "datasources") if f.endswith(".datasource")]
                for datasource_file in datasource_files:
                    datasource_path = Path(folder) / "datasources" / datasource_file
                    llm = LLM(user_token=user_token, host=tb_client.host)
                    datasource_name = datasource_path.stem
                    datasource_content = datasource_path.read_text()
                    has_json_path = "`json:" in datasource_content
                    if has_json_path:
                        prompt = f"<datasource_schema>{datasource_content}</datasource_schema>"
                        response = llm.ask(system_prompt=mock_prompt(rows), prompt=prompt)
                        sql = extract_xml(response, "sql")
                        sql = sql.split("FORMAT")[0]
                        query_result = await local_client.query(f"{sql} FORMAT JSON")
                        data = query_result.get("data", [])
                        fixture_name = build_fixture_name(
                            datasource_path.absolute().as_posix(), datasource_name, datasource_content
                        )
                        if data:
                            persist_fixture(fixture_name, data, folder)
                            click.echo(FeedbackManager.info(message=f"✓ /fixtures/{datasource_name}"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"Error: {str(e)}"))


PROJECT_PATHS = ("datasources", "endpoints", "materializations", "copies", "sinks", "fixtures", "tests")


def validate_project_structure(folder: str) -> bool:
    return all((Path(folder) / path).exists() for path in PROJECT_PATHS)


def should_generate_fixtures(result: str) -> bool:
    if not result:
        return False
    return "<type>datasource</type>" in result


def already_has_cicd(folder: str) -> bool:
    ci_cd_paths = (".gitlab", ".github")
    return any((Path(folder) / path).exists() for path in ci_cd_paths)


def already_has_cursor_rules(folder: str) -> bool:
    cursor_rules_paths = (".cursorrules", ".windsurfrules")
    return any((Path(folder) / path).exists() for path in cursor_rules_paths)


def create_project_structure(folder: str):
    folder_path = Path(folder)
    for x in PROJECT_PATHS:
        try:
            f = folder_path / x
            f.mkdir()
        except FileExistsError:
            pass
        click.echo(FeedbackManager.info_path_created(path=x))


async def create_resources(
    local_client: TinyB,
    tb_client: TinyB,
    user_token: Optional[str],
    data: Optional[str],
    prompt: Optional[str],
    folder: str,
    skip: bool,
):
    result = ""
    folder_path = Path(folder)
    if data:
        path = folder_path / data
        format = path.suffix.lstrip(".")
        await _generate_datafile(str(path), local_client, format=format, force=True)
        name = data.split(".")[0]
        generate_pipe_file(
            f"{name}_endpoint",
            f"""
NODE endpoint
SQL >
    SELECT * from {name}
TYPE ENDPOINT
            """,
            folder,
        )
        result = (
            f"<response><resource><type>datasource</type><name>{name}</name><content></content></resource></response>"
        )

    elif prompt and user_token:
        datasource_paths = [
            Path(folder) / "datasources" / f
            for f in os.listdir(Path(folder) / "datasources")
            if f.endswith(".datasource")
        ]
        pipes_paths = [
            Path(folder) / "endpoints" / f for f in os.listdir(Path(folder) / "endpoints") if f.endswith(".pipe")
        ]
        resources_xml = "\n".join(
            [
                f"<resource><type>{resource_type}</type><name>{resource_name}</name><content>{resource_content}</content></resource>"
                for resource_type, resource_name, resource_content in [
                    ("datasource", ds.stem, ds.read_text()) for ds in datasource_paths
                ]
                + [
                    (
                        "pipe",
                        pipe.stem,
                        pipe.read_text(),
                    )
                    for pipe in pipes_paths
                ]
            ]
        )
        llm = LLM(user_token=user_token, host=tb_client.host)
        result = ""
        iterations = 0
        history = ""
        generated_paths: list[Path] = []

        while iterations < 10:
            feedback = ""
            if iterations > 0:
                feedback = click.prompt("\nFollow-up instructions or continue", default="continue")
            if iterations > 0 and (not feedback or feedback in ("continue", "ok", "exit", "quit", "q")):
                break
            else:
                if iterations > 0:
                    click.echo(FeedbackManager.highlight(message="\n» Creating resources..."))
                    for path in generated_paths:
                        path.unlink()
                    generated_paths = []

                save_context(prompt, feedback)
                result = llm.ask(system_prompt=create_prompt(resources_xml, feedback, history), prompt=prompt)
                result = extract_xml(result, "response")
                history = (
                    history
                    + f"""
                <result_iteration_{iterations}>
                    {result}
                </result_iteration_{iterations}>
                """
                )
                resources = parse_xml(result, "resource")
                datasources = []
                pipes = []
                for resource_xml in resources:
                    resource_type = extract_xml(resource_xml, "type")
                    name = extract_xml(resource_xml, "name")
                    content = extract_xml(resource_xml, "content")
                    resource = {
                        "name": name,
                        "content": content,
                    }
                    if resource_type.lower() == "datasource":
                        datasources.append(resource)
                    elif resource_type.lower() == "pipe":
                        pipes.append(resource)

                for ds in datasources:
                    content = ds["content"].replace("```", "")
                    filename = f"{ds['name']}.datasource"
                    datasource_path = generate_datafile(
                        content,
                        filename=filename,
                        data=None,
                        _format="ndjson",
                        force=True,
                        folder=folder,
                    )
                    generated_paths.append(datasource_path)
                for pipe in pipes:
                    content = pipe["content"].replace("```", "")
                    pipe_path = generate_pipe_file(pipe["name"], content, folder)
                    generated_paths.append(pipe_path)
                if skip:
                    break
                iterations += 1

        if iterations == 10:
            click.echo(FeedbackManager.info(message="Too many iterations. Change the prompt and try again."))

        return result


def init_git(folder: str):
    try:
        path = Path(folder)
        gitignore_file = path / ".gitignore"

        if gitignore_file.exists():
            content = gitignore_file.read_text()
            if ".tinyb" not in content:
                gitignore_file.write_text(content + "\n.tinyb\n")
        else:
            gitignore_file.write_text(".tinyb\n")

        click.echo(FeedbackManager.info_file_created(file=".gitignore"))
    except Exception as e:
        raise CLIException(f"Error initializing Git: {e}")


def generate_pipe_file(name: str, content: str, folder: str) -> Path:
    def is_copy(content: str) -> bool:
        return re.search(r"TYPE copy", content, re.IGNORECASE) is not None

    def is_materialization(content: str) -> bool:
        return re.search(r"TYPE materialized", content, re.IGNORECASE) is not None

    def is_sink(content: str) -> bool:
        return re.search(r"TYPE sink", content, re.IGNORECASE) is not None

    if is_copy(content):
        pathname = "copies"
    elif is_materialization(content):
        pathname = "materializations"
    elif is_sink(content):
        pathname = "sinks"
    else:
        pathname = "endpoints"

    base = Path(folder) / pathname
    if not base.exists():
        base = Path()
    f = base / (f"{name}.pipe")
    with open(f"{f}", "w") as file:
        file.write(content)
    click.echo(FeedbackManager.info_file_created(file=f.relative_to(folder)))
    return f.relative_to(folder)


def create_rules(folder: str, source: str, agent: str):
    if agent == "cursor":
        extension = ".cursorrules"
    elif agent == "windsurf":
        extension = ".windsurfrules"
    else:
        extension = ".txt"
    rules_file = Path(folder) / extension
    rules_file.write_text(rules_prompt(source))


def get_context_file() -> Path:
    context_file = Path(os.path.expanduser("~/.tb_create_context"))
    if not context_file.exists():
        context_file.touch()
    return context_file


def get_context() -> str:
    context_file = get_context_file()
    return context_file.read_text()


def save_context(prompt: str, feedback: str):
    context_file = get_context_file()
    context_file.write_text(f"- {prompt}\n{feedback}")


@cli.command("rules")
@click.option("--agent", type=str, default="cursor", help="Agent to use for rules")
@click.option("--source", type=str, default="tb", help="Source of the command")
@click.pass_context
def rules(ctx: click.Context, agent: str, source: str):
    """Create agent rules for the project."""
    project: Project = ctx.ensure_object(dict)["project"]
    create_rules(str(project.path), source, agent)
