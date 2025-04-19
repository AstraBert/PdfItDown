from pdfconversion import Converter, MultipleFileConversion, OutputPath, FilePath
import os
from pydantic import ValidationError

TEST_FILES = ["./tests/data/"+f for f in os.listdir("./tests/data/") if not f.endswith(".txt")]

def test_multiplefileconversion_class():
    test_cases = [
        {
            "input_files": [FilePath(file=f) for f in TEST_FILES],
            "output_files": None,
            "expected": MultipleFileConversion(input_files=[FilePath(file=f) for f in TEST_FILES], output_files=[OutputPath(file=f.replace(os.path.splitext(f)[1], ".pdf")) for f in TEST_FILES]),
        },
        {
            "input_files": [FilePath(file=f) for f in TEST_FILES],
            "output_files": ["error.pdf"],
            "expected": None,
        },
        {
            "input_files": [FilePath(file=f) for f in TEST_FILES],
            "output_files": ["test_output"+str(i)+".pdf" for i in range(len(TEST_FILES))],
            "expected": MultipleFileConversion(input_files=[FilePath(file=f) for f in TEST_FILES], output_files=[OutputPath(file="test_output"+str(i)+".pdf") for i in range(len(TEST_FILES))]),
        }
    ]
    for c in test_cases:
        try:
            test_cls = MultipleFileConversion(input_files=c["input_files"], output_files=c["output_files"])
            assert test_cls == c["expected"]
        except ValidationError as e:
            assert None == c["expected"]

def test_multiple_files_conversion():
    converter = Converter()
    test_cases = [
        {
            "input_files": TEST_FILES,
            "output_files": None,
            "expected": [f.replace(os.path.splitext(f)[1], ".pdf") for f in TEST_FILES]
        },
        {
            "input_files": TEST_FILES,
            "output_files": ["error.pdf"],
            "expected": None
        },
        {
            "input_files": TEST_FILES,
            "output_files": ["./tests/data/test_output"+str(i)+".pdf" for i in range(len(TEST_FILES))],
            "expected": ["./tests/data/test_output"+str(i)+".pdf" for i in range(len(TEST_FILES))]
        }
    ]
    for c in test_cases:
        try:
            output_files = converter.multiple_convert(file_paths=c["input_files"], output_paths=c["output_files"])
            assert output_files == c["expected"]
            for f in output_files:
                os.remove(f)
        except ValidationError as e:
            assert None == c["expected"]
    