from pdfitdown_ui import to_pdf
import os
from pathlib import Path

def test_to_pdf():
    test_files = ["tests/data/test0.png", "tests/data/test1.csv", "tests/data/test2.md", "tests/data/test3.json", "tests/data/test.txt"]
    expected_outputs = ["tests/data/test0.pdf", "tests/data/test1.pdf", "tests/data/test2.pdf", "tests/data/test3.pdf"]
    assert to_pdf(test_files) == expected_outputs
    for p in expected_outputs:
        if Path(p).is_file():
            os.remove(p)

