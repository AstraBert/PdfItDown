from pathlib import Path
from pdfconversion import Converter
import os
from pydantic import ValidationError

def test_file_conversion():
    test_files = ["tests/data/test0.png", "tests/data/test1.csv", "tests/data/test2.md", "tests/data/test3.json"]
    test_error = "tests/data/test.txt"
    outputs = []
    expected_outputs = []
    converter = Converter()
    for test_file in test_files:
        ext = test_file.split(".")[1]
        output = test_file.replace(ext, "pdf")
        expected_outputs.append(output)
        result = converter.convert(test_file, output)
        outputs.append(result)
    error_thrown = "Initialization threw an error"
    expected_outputs.append(error_thrown)
    try:
        converter.convert(test_error, "test.pdf")
    except ValidationError:
        result_error = "Initialization threw an error"     
        outputs.append(result_error)
    error_thrown_1 = "Conversion threw an error"
    expected_outputs.append(error_thrown_1)
    try:
        converter.convert(test_files[0], "test.json")
    except ValidationError:
        result_error_1 = "Conversion threw an error"     
        outputs.append(result_error_1)
    for p in outputs:
        if Path(p).is_file():
            os.remove(p)
    assert outputs == expected_outputs