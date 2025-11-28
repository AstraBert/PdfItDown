import pytest
import os
from pathlib import Path
from collections import defaultdict
from pdfitdown.pdfconversion.models import ConversionCallback
from pdfitdown.pdfconversion.converter import Converter

CONVERTED_FILES = defaultdict(str)
CONVERTED_TITLES = []


@pytest.fixture()
def custom_conversion_callback() -> ConversionCallback:
    def mock_convert(
        input_file: str,
        output_file: str,
        title: str | None = None,
        overwrite: bool = True,
    ):
        global CONVERTED_FILES, CONVERTED_TITLES
        if overwrite:
            CONVERTED_FILES[input_file] = output_file
            CONVERTED_TITLES.append(title or "No title")
        else:
            if not CONVERTED_FILES[input_file]:
                CONVERTED_FILES[input_file] = output_file
                CONVERTED_TITLES.append(title or "No title")
            else:
                raise FileExistsError("Cannot overwrite file")

    return mock_convert


@pytest.fixture()
def text_file() -> str:
    return os.path.join("tests/data", "test.txt")


@pytest.fixture()
def image_file() -> str:
    return os.path.join("tests/data", "test0.png")


@pytest.fixture()
def to_convert_file() -> str:
    return os.path.join("tests/data", "test1.pptx")


@pytest.fixture()
def to_convert_dir() -> str:
    return "tests/data"


def test_conversion_callback_single_file(
    custom_conversion_callback: ConversionCallback, text_file: str
) -> None:
    converter = Converter(conversion_callback=custom_conversion_callback)
    converter.convert(
        text_file,
        text_file.replace(Path(text_file).suffix, ".pdf"),
        title="hello world",
    )
    assert CONVERTED_FILES[text_file] == text_file.replace(
        Path(text_file).suffix, ".pdf"
    )
    assert "hello world" in CONVERTED_TITLES
    converter.convert(
        text_file,
        text_file.replace(Path(text_file).suffix, ".1.pdf"),
        title="hello world 1",
    )
    assert CONVERTED_FILES[text_file] == text_file.replace(
        Path(text_file).suffix, ".1.pdf"
    )
    assert "hello world 1" in CONVERTED_TITLES
    with pytest.raises(FileExistsError, match="Cannot overwrite file"):
        converter.convert(
            text_file,
            text_file.replace(Path(text_file).suffix, ".1.pdf"),
            title="hello world 2",
            overwrite=False,
        )
    assert "hello world 2" not in CONVERTED_TITLES


def test_conversion_callback_multiple_files(
    custom_conversion_callback: ConversionCallback,
    image_file: str,
    to_convert_file: str,
) -> None:
    converter = Converter(conversion_callback=custom_conversion_callback)
    input_files = [image_file, to_convert_file]
    converter.multiple_convert(file_paths=input_files)
    assert CONVERTED_FILES[image_file] == image_file.replace(
        Path(image_file).suffix, ".pdf"
    )
    assert CONVERTED_FILES[to_convert_file] == to_convert_file.replace(
        Path(to_convert_file).suffix, ".pdf"
    )
    assert CONVERTED_TITLES.count("No title") == 2
    output_files = [
        image_file.replace(Path(image_file).suffix, ".1.pdf"),
        to_convert_file.replace(Path(to_convert_file).suffix, ".1.pdf"),
    ]
    converter.multiple_convert(file_paths=input_files, output_paths=output_files)
    assert CONVERTED_FILES[image_file] == image_file.replace(
        Path(image_file).suffix, ".1.pdf"
    )
    assert CONVERTED_FILES[to_convert_file] == to_convert_file.replace(
        Path(to_convert_file).suffix, ".1.pdf"
    )
    assert CONVERTED_TITLES.count("No title") == 4
    with pytest.raises(FileExistsError, match="Cannot overwrite file"):
        converter.multiple_convert(file_paths=input_files, overwrite=False)
    assert CONVERTED_TITLES.count("No title") == 4


def test_conversion_callback_directory(
    custom_conversion_callback: ConversionCallback, to_convert_dir: str
) -> None:
    global CONVERTED_FILES
    global CONVERTED_TITLES
    CONVERTED_TITLES.clear()
    CONVERTED_FILES.clear()
    converter = Converter(conversion_callback=custom_conversion_callback)
    converter.convert_directory(directory_path=to_convert_dir)
    assert len(CONVERTED_FILES) == len(
        [
            fl
            for fl in os.listdir(to_convert_dir)
            if os.path.isfile(os.path.join(to_convert_dir, fl))
        ]
    )
    assert CONVERTED_TITLES.count("No title") == len(
        [
            fl
            for fl in os.listdir(to_convert_dir)
            if os.path.isfile(os.path.join(to_convert_dir, fl))
        ]
    )
    for file in CONVERTED_FILES:
        assert CONVERTED_FILES[file] == file.replace(Path(file).suffix, ".pdf")
    with pytest.raises(FileExistsError, match="Cannot overwrite file"):
        converter.convert_directory(directory_path=to_convert_dir, overwrite=False)
