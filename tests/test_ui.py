from pdfitdown_ui import to_pdf
import os
from pathlib import Path

def test_to_pdf():
    test_files = ["tests/data/markitdown/test0.png","tests/data/markitdown/test.txt","tests/data/markitdown/test2.md"]
    expected_outputs = ["tests/data/markitdown/test0.pdf","tests/data/markitdown/test.pdf","tests/data/markitdown/test2.pdf"]
    assert to_pdf(test_files) == expected_outputs
    for p in expected_outputs:
        if Path(p).is_file():
            os.remove(p)

