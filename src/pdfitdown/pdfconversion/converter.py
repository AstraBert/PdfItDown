from .models import ConversionCallback, MultipleConversion, OsPath


class Converter:
    """
    Converter class for handling file and directory conversions using a customizable callback.

    Args:
        conversion_callback (ConversionCallback | None): Optional callback function for conversion.
            If not provided, defaults to `pdfitdown.pdfconversion._default_callback.convert_file`.
    """

    def __init__(self, conversion_callback: ConversionCallback | None = None):
        if conversion_callback is None:
            from ._default_callback import convert_file

            self._conversion_callback: ConversionCallback = convert_file
        else:
            self._conversion_callback = conversion_callback

    def convert(
        self,
        file_path: str,
        output_path: str,
        title: str | None = None,
        overwrite: bool = True,
    ) -> str | None:
        """
        Converts a file to PDF format using the specified conversion callback.

        Args:
            file_path (str): The path to the input file.
            output_path (str): The path where the converted PDF file will be saved.
            title (str | None, optional): An optional title for the converted PDF file. Defaults to None.
            overwrite (bool, optional): Whether to overwrite the output file if it already exists. Defaults to True.

        Returns:
            str | None: The path to the converted file if successful, otherwise None.
        """
        return self._conversion_callback(file_path, output_path, title, overwrite)

    def _multiple_convert(
        self,
        obj: MultipleConversion,
        overwrite: bool,
    ) -> list[str]:
        converted: list[str] = []
        for i, fl in enumerate(obj.input_files):
            conv = self._conversion_callback(
                fl.path, obj.output_files[i].path, None, overwrite
            )
            if conv is not None:
                converted.append(conv)
        return converted

    def multiple_convert(
        self,
        file_paths: list[str],
        output_paths: list[str] | None = None,
        overwrite: bool = True,
    ) -> list[str]:
        """
        Converts multiple input files using the specified conversion logic.

        Args:
            file_paths (list[str]): List of input file paths to be converted.
            output_paths (list[str] | None, optional): List of output file paths. If None, output paths are determined automatically. Defaults to None.
            overwrite (bool, optional): Whether to overwrite existing output files. Defaults to True.

        Returns:
            list[str]: List of output file paths after conversion.
        """
        if output_paths is None:
            multipleconv = MultipleConversion.from_input_files(file_paths, overwrite)
        else:
            multipleconv = MultipleConversion(
                input_files=[
                    OsPath.from_file(fl, overwrite, True) for fl in file_paths
                ],
                output_files=[
                    OsPath.from_file(fl, overwrite, False) for fl in output_paths
                ],
            )
        return self._multiple_convert(multipleconv, overwrite)

    def convert_directory(
        self,
        directory_path: str,
        overwrite: bool = True,
        recursive: bool = True,
    ):
        """
        Converts all files in the specified directory to the desired format.

        Args:
            directory_path (str): The path to the directory containing files to convert.
            overwrite (bool, optional): Whether to overwrite existing converted files. Defaults to True.
            recursive (bool, optional): Whether to include files in subdirectories recursively. Defaults to True.

        Returns:
            Result of the multiple file conversion process.
        """
        dirobj = OsPath.from_dir(directory_path, overwrite)
        multipleconv = MultipleConversion.from_directory(dirobj, recursive)
        return self._multiple_convert(multipleconv, overwrite)
