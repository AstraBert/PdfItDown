from ._default_callback import convert_file
from .models import ConversionCallback, MultipleConversion, OsPath


class Converter:
    def __init__(self, conversion_callback: ConversionCallback | None = None):
        self._conversion_callback: ConversionCallback = (
            conversion_callback or convert_file
        )

    def convert(
        self,
        file_path: str,
        output_path: str,
        title: str | None = None,
        overwrite: bool = True,
    ) -> str | None:
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
        dirobj = OsPath.from_dir(directory_path, overwrite)
        multipleconv = MultipleConversion.from_directory(dirobj, recursive)
        return self._multiple_convert(multipleconv, overwrite)
