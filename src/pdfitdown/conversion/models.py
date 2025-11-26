import os
import warnings
from dataclasses import dataclass, field
from typing import Literal
from pathlib import Path
from .errors import FileExistsWarning


@dataclass
class OsPath:
    path: str
    type: Literal["file", "directory", "outputfile"] = field(default="file")
    overwrite: bool = field(default=False)

    def __post_init__(self) -> None:
        if self.type == "file" and not Path(self.path).is_file():
            raise FileNotFoundError(f"No such file: {self.path}")
        elif self.type == "directory" and not Path(self.path).is_dir():
            raise FileNotFoundError(f"No such directory: {self.path}")
        elif (
            self.type == "directory"
            and Path(self.path).is_dir()
            and len(os.listdir(self.path)) == 0
        ):
            raise ValueError(
                f"Directory {self.path} exists but is empty. Provide a non-empty directory"
            )
        elif self.type == "outputfile" and Path(self.path).suffix != ".pdf":
            raise ValueError("You should provide a PDF file as output")
        elif self.type == "outputfile" and Path(self.path).is_file():
            if self.overwrite:
                warnings.warn(
                    f"File {self.path} already exists and will be overwritten",
                    FileExistsWarning,
                )
            else:
                raise FileExistsError(
                    f"File {self.path} already exists. If you wish to overwrite, please set `overwrite` to True"
                )
        else:
            return


@dataclass
class MultipleConversion:
    input_files: list[OsPath]
    output_files: list[OsPath]

    def __post_init__(self) -> None:
        if len(self.input_files) != len(self.output_files):
            raise ValueError(
                "There should be as many output files as there are input files"
            )
