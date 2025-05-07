from pdfitdown_ui import to_pdf
import os
from pathlib import Path

def test_to_pdf():
    test_files = ["tests/data/test0.png","tests/data/test.txt","tests/data/test2.md"]
    expected_outputs = ["tests/data/test0.pdf","tests/data/test.pdf","tests/data/test2.pdf"]
    assert to_pdf(test_files) == expected_outputs
    for p in expected_outputs:
        if Path(p).is_file():
            os.remove(p)
