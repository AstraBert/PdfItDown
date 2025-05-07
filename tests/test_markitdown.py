from pdfconversion import Converter
import pathlib
import os

converter = Converter()

def test_single_file():
    test_cases = [
        {
            "test_name": "Successful image conversion",
            "file_input": "tests/data/test0.png",
            "file_output": "tests/data/test0.pdf",
            "expected": True
        },
        {
            "test_name": "Successful text file conversion",
            "file_input": "tests/data/test.txt",
            "file_output": "tests/data/test.pdf",
            "expected": True
        },
        {
            "test_name": "Successful md file conversion",
            "file_input": "tests/data/test2.md",
            "file_output": "tests/data/test2.pdf",
            "expected": True
        },
        {
            "test_name": "Unsuccessful file conversion",
            "file_input": "tests/data/test1.pptx",
            "file_output": "tests/data/test1.pdf",
            "expected": True
        },
        {
            "test_name": "Unsuccessful file conversion",
            "file_input": "tests/data/tes.md",
            "file_output": "tests/data/tes.pdf",
            "expected": False
        },
    ]
    for c in test_cases:
        print(c["test_name"])
        try:
            result = converter.convert(file_path=c["file_input"], output_path=c["file_output"])
            assert pathlib.Path(result).is_file() == c["expected"]
            if pathlib.Path(result).is_file():
                os.remove(result)
        except Exception:
            result = c["file_output"]
            assert pathlib.Path(result).is_file() == c["expected"]

def test_multiple_files():
    test_cases = [
        {
            "test_name": "Specified output files",
            "file_input": ["tests/data/test0.png","tests/data/test.txt","tests/data/test2.md"],
            "file_output": ["tests/data/test0_1.pdf","tests/data/test_1.pdf","tests/data/test2_1.pdf"],
            "expected": [True, True, True]
        },
        {
            "test_name": "Unspecified output files",
            "file_input": ["tests/data/test0.png","tests/data/test.txt","tests/data/test2.md"],
            "file_output": None,
            "expected": [True, True, True]
        },
        {
            "test_name": "Unspecified output files",
            "file_input": ["tests/data/test0.png","tests/data/test.txt","tests/data/test2.md"],
            "file_output": ["tests/data/test0_2.pdf"],
            "expected": False
        },
    ]
    for c in test_cases:
        print(c["test_name"])
        try:
            result = converter.multiple_convert(file_paths=c["file_input"], output_paths=c["file_output"])
            assert [pathlib.Path(r).is_file() for r in result] == c["expected"]
            for f in result:
                if pathlib.Path(f).is_file():
                    os.remove(f)
        except Exception:
            assert pathlib.Path(c["file_output"][0]).is_file() == c["expected"]


def test_dir():
    test_cases = [
        {
            "test_name": "Correct dir path",
            "file_input": "tests/data",
            "file_output": ["tests/data/test0.pdf","tests/data/test1.pdf", "tests/data/test.pdf","tests/data/test2.pdf", "tests/data/test3.pdf", "tests/data/test4.pdf", "tests/data/test5.pdf"],
            "expected": [True, True, True, True, True, True, True]
        },
        {
            "test_name": "Wrong dir path",
            "file_input": "tests/dat",
            "file_output": ["tests/data/test0.pdf","tests/data/test1.pdf", "tests/data/test.pdf","tests/data/test2.pdf", "tests/data/test3.pdf", "tests/data/test4.pdf", "tests/data/test5.pdf"],
            "expected": [False, False, False, False, False, False, False]
        },
    ]
    for c in test_cases:
        print(c["test_name"])
        try:
            converter.convert_directory(directory_path=c["file_input"])
            assert [pathlib.Path(r).is_file() for r in c["file_output"]] == c["expected"]
            for f in c["file_output"]:
                if pathlib.Path(f).is_file():
                    os.remove(f)
        except Exception:
            assert [pathlib.Path(r).is_file() for r in c["file_output"]] == c["expected"]
