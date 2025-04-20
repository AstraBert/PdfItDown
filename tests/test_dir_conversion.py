from pdfconversion import Converter, DirPath
from pydantic import ValidationError
import os

def test_dirpath_model():
    test_cases = [
        {
            "path": "tests/data/testdir/",
            "expected": DirPath(path="tests/data/testdir/")
        },
        {
            "path": "tests/data/testdi/",
            "expected": None,
        },
    ]
    for c in test_cases:
        try:
            p = DirPath(path=c["path"])
            assert p == c["expected"]
        except ValidationError:
            assert None == c["expected"]

def test_dir_conversion():
    converter = Converter()
    test_cases = [
        {
            "path": "tests/data/testdir",
            "expected": ["tests/data/testdir/test.pdf", "tests/data/testdir/test1.pdf", "tests/data/testdir/test2.pdf"]
        },
        {
            "path": "tests/data/testdi/",
            "expected": None,
        },
    ]
    for c in test_cases:
        try:
            output_files = converter.convert_directory(c["path"])
            assert output_files == c["expected"]
            for f in output_files:
                os.remove(f)
        except ValidationError:
            assert None == c["expected"]
