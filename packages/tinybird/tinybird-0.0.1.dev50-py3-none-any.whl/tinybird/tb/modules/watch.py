import asyncio
import os
import time
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

import click
from watchdog.events import (
    DirDeletedEvent,
    DirMovedEvent,
    FileDeletedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
    PatternMatchingEventHandler,
)
from watchdog.observers import Observer

from tinybird.tb.modules.datafile.common import Datafile, DatafileKind
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.project import Project
from tinybird.tb.modules.shell import Shell


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filenames: List[str], process: Callable[[List[str]], None], build_ok: bool):
        self.unprocessed_filenames = [os.path.abspath(f) for f in filenames]
        self.process = process
        self.build_ok = build_ok

    @property
    def filenames(self) -> List[str]:
        return [f for f in self.unprocessed_filenames if os.path.exists(f)]

    def should_process(self, event: Any) -> Optional[str]:
        if event.is_directory:
            return None

        def should_process_path(path: str) -> bool:
            if not os.path.exists(path):
                return False
            is_vendor = "vendor/" in path
            if is_vendor:
                return False
            return any(path.endswith(ext) for ext in [".datasource", ".pipe", ".ndjson"])

        if should_process_path(event.src_path):
            return event.src_path

        if should_process_path(event.dest_path):
            return event.dest_path

        return None

    def on_modified(self, event: Any) -> None:
        if path := self.should_process(event):
            filename = path.split("/")[-1]
            click.echo(FeedbackManager.highlight(message=f"\n\n⟲ Changes detected in {filename}\n"))
            try:
                to_process = [path] if self.build_ok else self.filenames
                self.process(to_process)
                self.build_ok = True
            except Exception as e:
                click.echo(FeedbackManager.error_exception(error=e))

    def on_moved(self, event: Union[DirMovedEvent, FileMovedEvent]) -> None:
        if path := self.should_process(event):
            is_new_file = False
            if path not in self.unprocessed_filenames:
                is_new_file = True
                self.unprocessed_filenames.append(path)

            filename = path.split("/")[-1]
            if is_new_file:
                click.echo(FeedbackManager.highlight(message=f"\n\n⟲ New file detected: {filename}\n"))
            else:
                click.echo(FeedbackManager.highlight(message=f"\n\n⟲ Changes detected in {filename}\n"))
            try:
                should_rebuild_all = is_new_file or not self.build_ok
                to_process = self.filenames if should_rebuild_all else [path]
                self.process(to_process)
                self.build_ok = True
            except Exception as e:
                click.echo(FeedbackManager.error_exception(error=e))


def watch_files(
    filenames: List[str],
    process: Callable,
    shell: Shell,
    project: Project,
    build_ok: bool,
) -> None:
    # Handle both sync and async process functions
    async def process_wrapper(files: List[str]) -> None:
        click.echo(FeedbackManager.highlight(message="» Rebuilding project..."))
        time_start = time.time()
        if asyncio.iscoroutinefunction(process):
            await process(files, watch=True)
        else:
            process(files, watch=True)
        time_end = time.time()
        elapsed_time = time_end - time_start
        click.echo(
            FeedbackManager.success(message="\n✓ ")
            + FeedbackManager.gray(message=f"Rebuild completed in {elapsed_time:.1f}s")
        )
        shell.reprint_prompt()

    event_handler = FileChangeHandler(filenames, lambda f: asyncio.run(process_wrapper(f)), build_ok)
    observer = Observer()

    observer.schedule(event_handler, path=str(project.path), recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


class WatchProjectHandler(PatternMatchingEventHandler):
    def __init__(
        self,
        shell: Shell,
        project: Project,
        process: Callable[[Optional[str], Optional[str]], None],
    ):
        self.shell = shell
        self.project = project
        self.process = process
        self.datafiles = project.get_project_datafiles()
        super().__init__(
            patterns=[
                f"{project.path}/**/*.datasource",
                f"{project.path}/**/*.pipe",
                f"{project.path}/fixtures/*.ndjson",
            ],
            ignore_patterns=[f"{project.path}/vendor/"],
        )

    def should_process(self, event: Any) -> Optional[str]:
        if event.is_directory:
            return None

        if os.path.exists(event.src_path):
            return event.src_path

        if os.path.exists(event.dest_path):
            return event.dest_path

        return event.src_path

    def _process(self, path: Optional[str] = None) -> None:
        click.echo(FeedbackManager.highlight(message="» Rebuilding project..."))
        time_start = time.time()
        self.process(path, self.diff(path))
        time_end = time.time()
        elapsed_time = time_end - time_start
        click.echo(
            FeedbackManager.success(message="\n✓ ")
            + FeedbackManager.gray(message=f"Rebuild completed in {elapsed_time:.1f}s")
        )
        self.shell.reprint_prompt()

    def diff(self, path: Optional[str] = None) -> Optional[str]:
        if not path:
            return None

        current_datafile = self.datafiles.get(path, None)
        new_datafile = self.project.get_datafile(path)
        table_name = None
        if current_datafile and new_datafile:
            if current_datafile.kind == DatafileKind.datasource:
                table_name = self.datasource_diff(current_datafile, new_datafile)
            elif current_datafile.kind == DatafileKind.pipe:
                table_name = self.pipe_diff(current_datafile, new_datafile)

        self.refresh_datafiles()
        return table_name

    def refresh_datafiles(self) -> None:
        self.datafiles = self.project.get_project_datafiles()

    def datasource_diff(self, current_datafile: Datafile, new_datafile: Datafile) -> Optional[str]:
        current_schema = current_datafile.nodes[0].get("schema")
        new_schema = new_datafile.nodes[0].get("schema")
        if current_schema != new_schema:
            return current_datafile.nodes[0].get("name")
        return None

    def pipe_diff(self, current_datafile: Datafile, new_datafile: Datafile) -> Optional[str]:
        current_nodes = current_datafile.nodes
        current_sql_dict = {node.get("name"): node.get("sql") for node in current_nodes}
        new_nodes = new_datafile.nodes
        new_sql_dict = {node.get("name"): node.get("sql") for node in new_nodes}
        for node in new_sql_dict.keys():
            if node and node not in current_sql_dict:
                return node

        for node_name, sql in new_sql_dict.items():
            current_sql = current_sql_dict.get(node_name)
            if current_sql and current_sql != sql:
                return node_name

        return None

    def on_modified(self, event: Any) -> None:
        if path := self.should_process(event):
            filename = Path(path).name
            click.echo(FeedbackManager.highlight(message=f"\n\n⟲ Changes detected in {filename}\n"))
            self._process(path)

    def on_deleted(self, event: Union[DirDeletedEvent, FileDeletedEvent]) -> None:
        filename = Path(str(event.src_path)).name
        if event.is_directory:
            click.echo(FeedbackManager.highlight(message=f"\n\n⟲ Deleted directory: {filename}\n"))
        else:
            click.echo(FeedbackManager.highlight(message=f"\n\n⟲ Deleted file: {filename}\n"))
        self._process()


def watch_project(
    shell: Shell,
    process: Callable[[Optional[str], Optional[str]], None],
    project: Project,
) -> None:
    event_handler = WatchProjectHandler(shell=shell, project=project, process=process)
    observer = Observer()
    observer.schedule(event_handler, path=str(project.path), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
