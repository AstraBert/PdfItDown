use pdfitdown::{img::ImageConverter, office::OfficeConverter, types::Converter};

fn main() -> Result<(), std::io::Error> {
    let converter = ImageConverter {};
    converter.convert_to_file("img/logo.png", "img/logo.pdf")?;
    let office_converter = OfficeConverter {};
    office_converter.convert_to_file("tests/data/test.txt", "tests/data/test.pdf")?;
    office_converter.convert_to_file("tests/data/test4.docx", "tests/data/test4.pdf")?;
    office_converter.convert_to_file("tests/data/test7.xlsx", "tests/data/test7.pdf")?;
    office_converter.convert_to_file("tests/data/test1.pptx", "tests/data/test1.pdf")?;
    office_converter.convert_to_file("tests/data/test3.json", "tests/data/test3.pdf")
}
