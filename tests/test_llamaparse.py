from pdfconversion import Converter
import pathlib
import os
from dotenv import load_dotenv

load_dotenv()

converter = Converter(reader="llamaparse",llamacloud_api_key=os.getenv("llamacloud_api_key"))

def test_single_file():
    test_cases = [
        {
            "test_name": "Successful HTML conversion",
            "file_input": "tests/data/llamaparse/test0.pptx",
            "file_output": "tests/data/llamaparse/test0.pdf",
            "expected": True
        },
        {
            "test_name": "Successful DOCX file conversion",
            "file_input": "tests/data/llamaparse/test1.csv",
            "file_output": "tests/data/llamaparse/test1.pdf",
            "expected": True
        },
        {
            "test_name": "Successful md file conversion",
            "file_input": "tests/data/llamaparse/test2.md",
            "file_output": "tests/data/llamaparse/test2.pdf",
            "expected": True
        },
        {
            "test_name": "Successful image file conversion",
            "file_input": "tests/data/llamaparse/test3.png",
            "file_output": "tests/data/llamaparse/test3.png",
            "expected": True
        },
        {
            "test_name": "Unsuccessful file conversion",
            "file_input": "tests/data/llamaparse/tes.md",
            "file_output": "tests/data/llamaparse/tes.pdf",
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
        except Exception as e:
            result = c["file_output"]
            assert pathlib.Path(result).is_file() == c["expected"]

def test_multiple_files():
    test_cases = [
        {
            "test_name": "Specified output files",
            "file_input": ["tests/data/llamaparse/test0.pptx","tests/data/llamaparse/test1.csv","tests/data/llamaparse/test2.md"],
            "file_output": ["tests/data/llamaparse/test0_1.pdf","tests/data/llamaparse/test_1.pdf","tests/data/llamaparse/test2_1.pdf"],
            "expected": [True, True, True]
        },
        {
            "test_name": "Unspecified output files",
            "file_input": ["tests/data/llamaparse/test0.pptx","tests/data/llamaparse/test1.csv","tests/data/llamaparse/test2.md"],
            "file_output": None,
            "expected": [True, True, True]
        },
        {
            "test_name": "Unspecified output files",
            "file_input": ["tests/data/llamaparse/test0.pptx","tests/data/llamaparse/test1.csv","tests/data/llamaparse/test2.md"],
            "file_output": ["tests/data/llamaparse/test0_2.pdf"],
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
        except Exception as e:
            assert pathlib.Path(c["file_output"][0]).is_file() == c["expected"]
        

def test_dir():
    test_cases = [
        {
            "test_name": "Correct dir path",
            "file_input": "tests/data/llamaparse",
            "file_output": ["tests/data/llamaparse/test0.pdf","tests/data/llamaparse/test1.pdf","tests/data/llamaparse/test2.pdf", "tests/data/llamaparse/test3.pdf", "tests/data/llamaparse/test4.pdf"],
            "expected": [True, True, True, True, True]
        },
        {
            "test_name": "Wrong dir path",
            "file_input": "tests/data/docli",
            "file_output": ["tests/data/llamaparse/test0.pdf","tests/data/llamaparse/test1.pdf","tests/data/llamaparse/test2.pdf", "tests/data/llamaparse/test3.pdf", "tests/data/llamaparse/test4.pdf"],
            "expected": [False, False, False, False, False]
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
        except Exception as e:
            assert [pathlib.Path(r).is_file() for r in c["file_output"]] == c["expected"]