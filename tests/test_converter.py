import pytest
import os
from pathlib import Path
from pdfitdown.pdfconversion.converter import Converter


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


@pytest.fixture()
def pdf_file() -> str:
    return os.path.join("tests/data", "outputfiles", "sample.pdf")


@pytest.fixture()
def all_files() -> list[str]:
    initial_files = [
        "test.txt",
        "test0.png",
        "test1.pptx",
        "test2.md",
        "test3.json",
        "test4.docx",
        "test5.zip",
        "test6.xml",
        "test7.xlsx",
    ]
    return [os.path.join("tests/data", file) for file in initial_files]


@pytest.fixture()
def converter() -> Converter:
    return Converter()


def test_converter_text_file(text_file: str, converter: Converter) -> None:
    converter.convert(
        file_path=text_file,
        output_path=text_file.replace(Path(text_file).suffix, ".pdf"),
        title="hello world",
    )
    assert Path(text_file.replace(Path(text_file).suffix, ".pdf")).exists()
    with open(text_file.replace(Path(text_file).suffix, ".pdf"), "rb") as f:
        bts = f.read()
    assert len(bts) > 0
    os.remove(text_file.replace(Path(text_file).suffix, ".pdf"))


def test_converter_pdf_file(pdf_file: str, converter: Converter) -> None:
    converter.convert(
        file_path=pdf_file,
        output_path=str(pdf_file.replace(Path(pdf_file).suffix, ".1.pdf")),
        title="hello world",
    )
    assert Path(pdf_file.replace(Path(pdf_file).suffix, ".1.pdf")).exists()
    with open(pdf_file.replace(Path(pdf_file).suffix, ".1.pdf"), "rb") as f:
        bts = f.read()
    assert len(bts) > 0
    with open(pdf_file, "rb") as f:
        content = f.read()
    assert bts == content
    os.remove(pdf_file.replace(Path(pdf_file).suffix, ".1.pdf"))


def test_converter_nontext_file(to_convert_file: str, converter: Converter) -> None:
    converter.convert(
        file_path=to_convert_file,
        output_path=str(to_convert_file.replace(Path(to_convert_file).suffix, ".pdf")),
        title="hello world",
    )
    assert Path(to_convert_file.replace(Path(to_convert_file).suffix, ".pdf")).exists()
    with open(to_convert_file.replace(Path(to_convert_file).suffix, ".pdf"), "rb") as f:
        bts = f.read()
    assert len(bts) > 0
    os.remove(to_convert_file.replace(Path(to_convert_file).suffix, ".pdf"))


def test_converter_image_file(image_file: str, converter: Converter) -> None:
    converter.convert(
        file_path=image_file,
        output_path=str(image_file.replace(Path(image_file).suffix, ".pdf")),
        title="hello world",
    )
    assert Path(image_file.replace(Path(image_file).suffix, ".pdf")).exists()
    with open(image_file.replace(Path(image_file).suffix, ".pdf"), "rb") as f:
        bts = f.read()
    assert len(bts) > 0
    os.remove(image_file.replace(Path(image_file).suffix, ".pdf"))


def test_converter_singlefile_erorr(text_file: str, converter: Converter) -> None:
    converter.convert(
        file_path=text_file,
        output_path=text_file.replace(Path(text_file).suffix, ".pdf"),
        title="hello world",
    )
    with pytest.raises(FileExistsError):
        converter.convert(
            file_path=text_file,
            output_path=text_file.replace(Path(text_file).suffix, ".pdf"),
            title="hello world",
            overwrite=False,
        )
    with pytest.raises(FileNotFoundError):
        converter.convert(
            file_path=text_file + "t",
            output_path=str(text_file.replace(Path(text_file).suffix, ".1.pdf")),
            title="hello world",
        )
    os.remove(text_file.replace(Path(text_file).suffix, ".pdf"))


def test_converter_multiple_files_default(
    all_files: list[str], converter: Converter
) -> None:
    converter.multiple_convert(file_paths=all_files)
    for file in all_files:
        p = Path(file)
        assert Path(file.replace(p.suffix, ".pdf")).exists()
        bts = Path(file.replace(p.suffix, ".pdf")).read_bytes()
        assert len(bts) > 0
        os.remove(file.replace(p.suffix, ".pdf"))


def test_converter_multiple_files_custom(
    all_files: list[str], converter: Converter
) -> None:
    all_files_output = [fl.replace(Path(fl).suffix, ".1.pdf") for fl in all_files]
    converter.multiple_convert(file_paths=all_files, output_paths=all_files_output)
    for file in all_files_output:
        assert Path(file).exists()
        bts = Path(file).read_bytes()
        assert len(bts) > 0
        os.remove(file)


def test_convert_multiple_files_error(
    all_files: list[str], converter: Converter
) -> None:
    all_files_output = [fl.replace(Path(fl).suffix, ".1.pdf") for fl in all_files[:-1]]
    with pytest.raises(ValueError):
        converter.multiple_convert(all_files, all_files_output)


def test_convert_directory(
    to_convert_dir: str, converter: Converter, all_files: list[str]
) -> None:
    converter.convert_directory(directory_path=to_convert_dir)
    with pytest.raises(FileExistsError):
        converter.convert_directory(directory_path=to_convert_dir, overwrite=False)
    for file in all_files:
        p = Path(file)
        assert Path(file.replace(p.suffix, ".pdf")).exists()
        bts = Path(file.replace(p.suffix, ".pdf")).read_bytes()
        assert len(bts) > 0
        os.remove(file.replace(p.suffix, ".pdf"))
