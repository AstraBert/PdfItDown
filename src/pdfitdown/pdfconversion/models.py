import os
import warnings
from dataclasses import dataclass, field
from typing import Literal, TypeAlias, Callable
from pathlib import Path
from .errors import FileExistsWarning

ConversionCallback: TypeAlias = Callable[[str, str, str | None, bool], str | None]


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

    @property
    def file_type(self) -> Literal["image", "text", "toconvert", "pdf", "none"]:
        if self.type != "file":
            return "none"
        suff = Path(self.path).suffix
        if suff in [".jpg", ".png"]:
            return "image"
        elif suff == ".pdf":
            return "pdf"
        elif suff in [".docx", ".xlsx", ".xls", ".pptx", ".zip"]:
            return "toconvert"
        else:
            return "text"

    @classmethod
    def from_file(cls, file: str, overwrite: bool, is_input: bool) -> "OsPath":
        if is_input:
            return cls(path=file, type="file", overwrite=overwrite)
        else:
            return cls(path=file, type="outputfile", overwrite=overwrite)

    @classmethod
    def from_dir(cls, directory: str, overwrite: bool) -> "OsPath":
        return cls(path=directory, type="directory", overwrite=overwrite)

    def read_file(self) -> str | bytes | None:
        if self.file_type == "text":
            with open(self.path, "r") as f:
                return f.read()
        elif self.file_type == "pdf":
            with open(self.path, "rb") as f:
                return f.read()
        return None

    def write_file(self, content: bytes) -> None:
        if self.type != "outputfile":
            return None
        if not self.overwrite:
            raise FileExistsError(
                f"File {self.path} already exists and cannot be overwritten. If you wish to overwrite, please set `overwrite` to True"
            )
        with open(self.path, "wb") as f:
            f.write(content)
        return None


@dataclass
class MultipleConversion:
    input_files: list[OsPath]
    output_files: list[OsPath]

    def __post_init__(self) -> None:
        if len(self.input_files) != len(self.output_files):
            raise ValueError(
                "There should be as many output files as there are input files"
            )

    @classmethod
    def from_directory(cls, directory: OsPath, recursive: bool) -> "MultipleConversion":
        inpt_files: list[OsPath] = []
        outpt_files: list[OsPath] = []
        if recursive:
            for root, _, files in os.walk(directory.path):
                if files:
                    for file in files:
                        if (suffix := Path(file).suffix) != ".pdf":
                            ifl = OsPath.from_file(
                                os.path.join(root, file), directory.overwrite, True
                            )
                            ofl = OsPath.from_file(
                                os.path.join(root, file.replace(suffix, ".pdf")),
                                directory.overwrite,
                                False,
                            )
                            inpt_files.append(ifl)
                            outpt_files.append(ofl)
        else:
            for fl in os.listdir(directory.path):
                if Path(fl).is_file() and (suffix := Path(fl).suffix) != ".pdf":
                    inpt_files.append(
                        OsPath.from_file(
                            os.path.join(directory.path, fl), directory.overwrite, True
                        )
                    )
                    outpt_files.append(
                        OsPath.from_file(
                            os.path.join(directory.path, fl.replace(suffix, ".pdf")),
                            directory.overwrite,
                            True,
                        )
                    )
        return cls(input_files=inpt_files, output_files=outpt_files)

    @classmethod
    def from_input_files(
        cls, input_files: list[str], overwrite: bool
    ) -> "MultipleConversion":
        inpt_files: list[OsPath] = []
        outpt_files: list[OsPath] = []
        for file in input_files:
            if (suffix := Path(file).suffix) != ".pdf":
                ifl = OsPath.from_file(file, overwrite, True)
                ofl = OsPath.from_file(file.replace(suffix, ".pdf"), overwrite, False)
                inpt_files.append(ifl)
                outpt_files.append(ofl)
        return cls(input_files=inpt_files, output_files=outpt_files)
