import pytest
import os

from pathlib import Path
from typer.testing import CliRunner
from pdfitdown.cli.app import app


@pytest.fixture()
def to_convert_file() -> str:
    return os.path.join("tests/data", "test1.pptx")


@pytest.fixture()
def to_convert_dir() -> str:
    return "tests/data"


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


@pytest.fixture(scope="module")
def runner() -> CliRunner:
    return CliRunner()


def test_cli_single_conversion(to_convert_file: str, runner: CliRunner) -> None:
    result = runner.invoke(app, ["--inputfile", to_convert_file])
    assert result.return_value is None
    assert result.output == "Conversion successful!🎉\n"
    assert Path(to_convert_file.replace(Path(to_convert_file).suffix, ".pdf")).exists()
    os.remove(to_convert_file.replace(Path(to_convert_file).suffix, ".pdf"))
    result = runner.invoke(
        app,
        [
            "--inputfile",
            to_convert_file,
            "--outputfile",
            to_convert_file.replace(Path(to_convert_file).suffix, ".1.pdf"),
        ],
    )
    assert result.return_value is None
    assert result.output == "Conversion successful!🎉\n"
    assert Path(
        to_convert_file.replace(Path(to_convert_file).suffix, ".1.pdf")
    ).exists()
    os.remove(to_convert_file.replace(Path(to_convert_file).suffix, ".1.pdf"))
    result = runner.invoke(
        app,
        [
            "--inputfile",
            to_convert_file,
            "--outputfile",
            to_convert_file.replace(Path(to_convert_file).suffix, ".1.pdf"),
            "--directory",
            "hello",
        ],
    )
    assert (
        result.output
        == "WARNING: `--directory` will be ignored since `--inputfile` has been provided\nConversion successful!🎉\n"
    )
    os.remove(to_convert_file.replace(Path(to_convert_file).suffix, ".1.pdf"))


def test_cli_multiple_conversion(all_files: list[str], runner: CliRunner) -> None:
    all_files_args = []
    for file in all_files:
        all_files_args.append("--inputfile")
        all_files_args.append(file)
    result = runner.invoke(app, all_files_args)
    assert result.return_value is None
    assert result.output == "Conversion successful!🎉\n"
    for file in all_files:
        assert Path(file.replace(Path(file).suffix, ".pdf")).exists()
        os.remove(file.replace(Path(file).suffix, ".pdf"))
    output_files_args = []
    for file in all_files:
        output_files_args.append("--outputfile")
        output_files_args.append(file.replace(Path(file).suffix, ".1.pdf"))
    result = runner.invoke(app, all_files_args + output_files_args)
    assert result.return_value is None
    assert result.output == "Conversion successful!🎉\n"
    for file in output_files_args:
        if file != "--outputfile":
            assert Path(file).exists()
            os.remove(file)
    result = runner.invoke(
        app, all_files_args + output_files_args + ["--title", "hello"]
    )
    assert result.return_value is None
    assert (
        result.output.replace("\n", "")
        == "WARNING: `--title` will be ignored since more than one `--inputfile` has been providedConversion successful!🎉"
    )
    for file in output_files_args:
        if file != "--outputfile":
            os.remove(file)
    result = runner.invoke(app, all_files_args + output_files_args[:-2])
    assert (
        result.output
        == "ERROR! `--inputfile` and `--outputfile` should be the same number\n"
    )
    assert result.exit_code == 1


def test_cli_directory(
    to_convert_dir: str, runner: CliRunner, all_files: list[str]
) -> None:
    result = runner.invoke(app, ["--directory", to_convert_dir])
    assert result.return_value is None
    assert result.output == "Conversion successful!🎉\n"
    for file in all_files:
        assert Path(file.replace(Path(file).suffix, ".pdf")).exists()
        os.remove(file.replace(Path(file).suffix, ".pdf"))
    result = runner.invoke(
        app, ["--directory", to_convert_dir, "--outputfile", "hello"]
    )
    assert (
        result.output.replace("\n", "")
        == "WARNING: `--outputfile` will be ignored since  `--inputfile` has not been providedConversion successful!🎉"
    )
    for file in all_files:
        os.remove(file.replace(Path(file).suffix, ".pdf"))
    result = runner.invoke(app, ["--directory", to_convert_dir, "--title", "hello"])
    assert (
        result.output.replace("\n", "")
        == "WARNING: `--title` will be ignored since `--directory` has been providedConversion successful!🎉"
    )
    for file in all_files:
        os.remove(file.replace(Path(file).suffix, ".pdf"))


def test_cli_errors(
    runner: CliRunner, to_convert_file: str, to_convert_dir: str
) -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 1
    assert (
        result.output
        == "ERROR! You should provide one of `--inputfile` or `--directory`\n"
    )
    result = runner.invoke(app, ["--directory", "doesnotexist"])
    assert result.exit_code == 2
    assert "ERROR during the conversion: " in result.output
    os.makedirs(os.path.join(to_convert_dir, "empty"), exist_ok=True)
    result = runner.invoke(app, ["--directory", os.path.join(to_convert_dir, "empty")])
    assert result.exit_code == 2
    assert "ERROR during the conversion: " in result.output
    result = runner.invoke(app, ["--inputfile", "doesnotexist.txt"])
    assert result.exit_code == 2
    assert "ERROR during the conversion: " in result.output
    result = runner.invoke(
        app,
        ["--inputfile", to_convert_file, "--inputfile", "doesnotexist.txt"],
    )
    assert result.exit_code == 2
    assert "ERROR during the conversion: " in result.output
