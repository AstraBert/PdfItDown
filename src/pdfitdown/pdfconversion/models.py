import os
import warnings
from dataclasses import dataclass, field
from typing import Literal, TypeAlias, Callable
from pathlib import Path
from .errors import FileExistsWarning

ConversionCallback: TypeAlias = Callable[[str, str, str | None, bool], str | None]


@dataclass
class OsPath:
    """
    Represents a filesystem path with type and overwrite options.

    Attributes:
        path (str): The filesystem path.
        type (Literal["file", "directory", "outputfile"]): The type of path, defaults to "file".
        overwrite (bool): Whether to overwrite an existing file, defaults to False.
    """

    path: str
    type: Literal["file", "directory", "outputfile"] = field(default="file")
    overwrite: bool = field(default=False)

    def __post_init__(self) -> None:
        """
        Validates the path based on its type after initialization.

        Raises:
            FileNotFoundError: If the specified file or directory does not exist.
            ValueError: If the directory is empty or output file is not a PDF.
            FileExistsError: If the output file exists and overwrite is False.
            FileExistsWarning: If the output file exists and overwrite is True.
        """
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
        """
        Determines the file type based on the file extension.

        Returns:
            Literal["image", "text", "toconvert", "pdf", "none"]: The type of the file.
        """
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
        """
        Creates an OsPath instance for a file or output file.

        Args:
            file (str): The file path.
            overwrite (bool): Whether to overwrite the file if it exists.
            is_input (bool): True if the file is an input file, False if output.

        Returns:
            OsPath: An instance of OsPath.
        """
        if is_input:
            return cls(path=file, type="file", overwrite=overwrite)
        else:
            return cls(path=file, type="outputfile", overwrite=overwrite)

    @classmethod
    def from_dir(cls, directory: str, overwrite: bool) -> "OsPath":
        """
        Creates an OsPath instance for a directory.

        Args:
            directory (str): The directory path.
            overwrite (bool): Whether to overwrite the output files if they exists.

        Returns:
            OsPath: An instance of OsPath.
        """
        return cls(path=directory, type="directory", overwrite=overwrite)

    def read_file(self) -> str | bytes | None:
        """
        Reads the file content based on its type.

        Returns:
            str | bytes | None: The content of the file as string (for text) or bytes (for PDF), or None if not readable.
        """
        if self.file_type == "text":
            with open(self.path, "r") as f:
                return f.read()
        elif self.file_type == "pdf":
            with open(self.path, "rb") as f:
                return f.read()
        return None

    def write_file(self, content: bytes) -> None:
        """
        Writes content to the output file if overwrite is enabled.

        Args:
            content (bytes): The content to write.

        Raises:
            FileExistsError: If the file exists and overwrite is False.
        """
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
    """
    Represents a batch conversion process for multiple files to PDF format.

    Attributes:
        input_files (list[OsPath]): List of input file paths to be converted.
        output_files (list[OsPath]): List of output file paths for the converted PDFs.
    """

    input_files: list[OsPath]
    output_files: list[OsPath]

    def __post_init__(self) -> None:
        if len(self.input_files) != len(self.output_files):
            raise ValueError(
                "There should be as many output files as there are input files"
            )

    @classmethod
    def from_directory(cls, directory: OsPath, recursive: bool) -> "MultipleConversion":
        """
        Creates a MultipleConversion instance from all non-PDF files in a given directory.

        Args:
            directory (OsPath): The directory to search for files.
            recursive (bool): If True, search subdirectories recursively; otherwise, only search the top-level directory.

        Returns:
            MultipleConversion: An instance containing input and output file paths for conversion.

        Notes:
            - Only files that do not have a '.pdf' suffix are considered for conversion.
            - For each input file, an output file path is generated by replacing its suffix with '.pdf'.
            - The overwrite flag from the directory is passed to OsPath.from_file.
        """
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
        """
        Creates a MultipleConversion instance from a list of input file paths.

        For each file in `input_files` that does not have a '.pdf' suffix, constructs
        corresponding OsPath objects for input and output files. The output file path
        is generated by replacing the original file's suffix with '.pdf'.

        Args:
            input_files (list[str]): List of input file paths.
            overwrite (bool): Whether to overwrite existing files.

        Returns:
            MultipleConversion: An instance with populated input and output OsPath lists.
        """
        inpt_files: list[OsPath] = []
        outpt_files: list[OsPath] = []
        for file in input_files:
            if (suffix := Path(file).suffix) != ".pdf":
                ifl = OsPath.from_file(file, overwrite, True)
                ofl = OsPath.from_file(file.replace(suffix, ".pdf"), overwrite, False)
                inpt_files.append(ifl)
                outpt_files.append(ofl)
        return cls(input_files=inpt_files, output_files=outpt_files)
