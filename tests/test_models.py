import pytest
import os
from pathlib import Path
from pdfitdown.pdfconversion.models import OsPath, MultipleConversion
from pdfitdown.pdfconversion.errors import FileExistsWarning


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


def test_ospath_text(text_file: str) -> None:
    path = OsPath(path=text_file, type="file", overwrite=True)
    assert path.file_type == "text"
    with open(text_file, "r") as f:
        content = f.read()
    assert content == path.read_file()


def test_ospath_image(image_file: str) -> None:
    path = OsPath(path=image_file, type="file", overwrite=True)
    assert path.file_type == "image"


def test_ospath_toconvert(to_convert_file: str) -> None:
    path = OsPath(path=to_convert_file, type="file", overwrite=True)
    assert path.file_type == "toconvert"


def test_ospath_pdf(pdf_file: str) -> None:
    path = OsPath(path=pdf_file, type="file", overwrite=True)
    assert path.file_type == "pdf"
    with open(pdf_file, "rb") as f:
        content = f.read()
    assert path.read_file() == content
    with pytest.warns(FileExistsWarning):
        path = OsPath(path=pdf_file, type="outputfile", overwrite=True)
    path.write_file(content=content)
    with open(pdf_file, "rb") as f:
        content1 = f.read()
    assert content1 == content
    with pytest.raises(FileExistsError):
        path.overwrite = False
        path.write_file(content=content)


def test_ospath_notype(to_convert_dir: str, text_file: str) -> None:
    path = OsPath(path=to_convert_dir, type="directory", overwrite=True)
    assert path.file_type == "none"
    path = OsPath(
        path=text_file.replace(".txt", ".pdf"), type="outputfile", overwrite=True
    )
    assert path.file_type == "none"


def test_ospath_validation(to_convert_dir: str, text_file: str, pdf_file: str):
    with pytest.raises(FileNotFoundError):
        OsPath(path=text_file[:-2], type="file", overwrite=True)
    with pytest.raises(FileNotFoundError):
        OsPath(path=to_convert_dir[:-2], type="directory", overwrite=True)
    os.makedirs("tests/data/empty", exist_ok=True)
    with pytest.raises(ValueError):
        OsPath(path="tests/data/empty", type="directory", overwrite=True)
    with pytest.raises(ValueError):
        OsPath(path=text_file, type="outputfile", overwrite=True)
    with pytest.raises(FileExistsError):
        OsPath(path=pdf_file, type="outputfile", overwrite=False)


def test_ospath_from_file(
    text_file: str, pdf_file: str, image_file: str, to_convert_file: str
) -> None:
    path = OsPath.from_file(file=text_file, overwrite=True, is_input=True)
    assert path.file_type == "text"
    assert path.type == "file"
    with pytest.raises(ValueError):
        OsPath.from_file(file=text_file, overwrite=True, is_input=False)
    path = OsPath.from_file(file=image_file, overwrite=True, is_input=True)
    assert path.file_type == "image"
    assert path.type == "file"
    with pytest.raises(ValueError):
        OsPath.from_file(file=image_file, overwrite=True, is_input=False)
    path = OsPath.from_file(file=to_convert_file, overwrite=True, is_input=True)
    assert path.file_type == "toconvert"
    assert path.type == "file"
    with pytest.raises(ValueError):
        OsPath.from_file(file=to_convert_file, overwrite=True, is_input=False)
    path = OsPath.from_file(file=pdf_file, overwrite=True, is_input=True)
    assert path.file_type == "pdf"
    assert path.type == "file"
    with pytest.warns(FileExistsWarning):
        path = OsPath.from_file(file=pdf_file, overwrite=True, is_input=False)
    assert path.type == "outputfile"
    assert path.file_type == "none"
    with pytest.raises(FileExistsError):
        OsPath.from_file(file=pdf_file, overwrite=False, is_input=False)


def test_ospath_from_dir(to_convert_dir: str) -> None:
    path = OsPath.from_dir(to_convert_dir, True)
    assert path.type == "directory"
    assert path.file_type == "none"
    with pytest.raises(FileNotFoundError):
        path = OsPath.from_dir(to_convert_dir[:-2], True)
    os.makedirs("tests/data/empty", exist_ok=True)
    with pytest.raises(ValueError):
        path = OsPath.from_dir("tests/data/empty", True)


def test_multipleconversion_validation(all_files: list[str]) -> None:
    all_files_input = [
        OsPath.from_file(file, overwrite=True, is_input=True) for file in all_files
    ]
    all_files_output = [
        OsPath.from_file(
            file.replace(Path(file).suffix, ".pdf"), overwrite=True, is_input=False
        )
        for file in all_files
    ]
    mc = MultipleConversion(input_files=all_files_input, output_files=all_files_output)
    assert mc.input_files == all_files_input
    assert mc.output_files == all_files_output
    with pytest.raises(ValueError):
        mc = MultipleConversion(
            input_files=all_files_input, output_files=all_files_output[:2]
        )


def test_multipleconversion_from_list(all_files: list[str]) -> None:
    mc = MultipleConversion.from_input_files(all_files, True)
    all_files_input = [
        OsPath.from_file(file, overwrite=True, is_input=True) for file in all_files
    ]
    all_files_output = [
        OsPath.from_file(
            file.replace(Path(file).suffix, ".pdf"), overwrite=True, is_input=False
        )
        for file in all_files
    ]
    assert mc.input_files == all_files_input
    assert mc.output_files == all_files_output
    with pytest.raises(FileNotFoundError):
        MultipleConversion.from_input_files([all_files[0] + "t", *all_files[1:]], True)


def test_multipleconversion_from_dir(
    to_convert_dir: str, pdf_file: str, all_files: str
) -> None:
    mc = MultipleConversion.from_directory(
        directory=OsPath.from_dir(to_convert_dir, True), recursive=True
    )
    for fl in mc.input_files:
        assert pdf_file not in fl.path
        assert fl.type == "file"
    for fl in mc.output_files:
        assert fl.path.endswith(".pdf")
        assert fl.type == "outputfile"
    assert len(mc.input_files) == len(all_files)
