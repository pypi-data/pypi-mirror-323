import glob
import os
from pathlib import Path
from typing import Dict, List, Optional

from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.datafile.common import Datafile
from tinybird.tb.modules.datafile.parse_datasource import parse_datasource
from tinybird.tb.modules.datafile.parse_pipe import parse_pipe


class Project:
    extensions = ("datasource", "pipe")

    def __init__(self, folder: Optional[str] = None):
        self.folder = folder or os.getcwd()
        self.path = Path(self.folder)

    def get_config(self) -> CLIConfig:
        return CLIConfig.get_project_config(self.folder)

    @property
    def vendor_path(self) -> str:
        return f"{self.path}/vendor"

    def get_project_files(self) -> List[str]:
        project_files: List[str] = []
        for extension in self.extensions:
            for project_file in glob.glob(f"{self.path}/**/*.{extension}", recursive=True):
                if self.vendor_path in project_file:
                    continue
                project_files.append(project_file)
        return project_files

    def get_vendor_files(self) -> List[str]:
        vendor_files: List[str] = []
        for project_file in glob.glob(f"{self.vendor_path}/**/*.datasource", recursive=True):
            vendor_files.append(project_file)
        return vendor_files

    @property
    def datasources(self) -> List[str]:
        return sorted([Path(f).stem for f in glob.glob(f"{self.path}/**/*.datasource", recursive=True)])

    @property
    def pipes(self) -> List[str]:
        return sorted([Path(f).stem for f in glob.glob(f"{self.path}/**/*.pipe", recursive=True)])

    def get_pipe_datafile(self, filename: str) -> Optional[Datafile]:
        try:
            return parse_pipe(filename)
        except Exception:
            return None

    def get_datasource_datafile(self, filename: str) -> Optional[Datafile]:
        try:
            return parse_datasource(filename)
        except Exception:
            return None

    def get_datafile(self, filename: str) -> Optional[Datafile]:
        if filename.endswith(".pipe"):
            return self.get_pipe_datafile(filename)
        elif filename.endswith(".datasource"):
            return self.get_datasource_datafile(filename)
        return None

    def get_project_datafiles(self) -> Dict[str, Datafile]:
        project_filenames = self.get_project_files()
        datafiles: Dict[str, Datafile] = {}
        for filename in project_filenames:
            if datafile := self.get_datafile(filename):
                datafiles[filename] = datafile
        return datafiles
