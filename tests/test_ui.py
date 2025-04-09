from pdfitdown_ui import to_pdf

def test_to_pdf():
    test_files = ["tests/data/test0.png", "tests/data/test1.csv", "tests/data/test2.md", "tests/data/test.txt"]
    expected_outputs = ["tests/data/test0.pdf", "tests/data/test1.pdf", "tests/data/test2.pdf"]
    assert to_pdf(test_files) == expected_outputs

