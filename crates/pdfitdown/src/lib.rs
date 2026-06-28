mod img;
mod markup;
mod office;
mod text;
pub mod types;

use std::{fs, io};

pub use img::ImageConverter;
pub use markup::MarkupConverter;
pub use office::OfficeConverter;
pub use text::TextConverter;

use crate::types::Converter;

#[derive(Debug, Clone, Copy, Default)]
pub struct PdfItDownConverter {
    markup_converter: MarkupConverter,
    office_converter: OfficeConverter,
    text_converter: TextConverter,
    image_converter: ImageConverter,
}

impl PdfItDownConverter {
    pub fn new() -> Self {
        PdfItDownConverter {
            markup_converter: MarkupConverter {},
            office_converter: OfficeConverter {},
            text_converter: TextConverter::new(),
            image_converter: ImageConverter {},
        }
    }
}

impl Converter for PdfItDownConverter {
    fn supported_formats(&self) -> &'static [&'static str] {
        self.image_converter
            .supported_formats()
            .iter()
            .chain(self.office_converter.supported_formats().iter())
            .chain(self.markup_converter.supported_formats().iter())
            .chain(self.text_converter.supported_formats().iter())
            .chain(["pdf"].iter())
            .copied()
            .collect::<Vec<&'static str>>()
            .leak()
    }

    fn convert(&self, input: impl Into<types::ConversionInput> + Clone) -> io::Result<Vec<u8>> {
        let extension;
        match input.clone().into() {
            types::ConversionInput::Binary(b) => {
                let kind = infer::get(&b);
                if let Some(k) = kind
                    && self
                        .supported_formats()
                        .contains(&k.extension().to_lowercase().as_str())
                {
                    extension = k.extension().to_lowercase();
                } else {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidData,
                        "Inferred file type is not supported",
                    ));
                }
            }
            types::ConversionInput::File(f) => {
                if let Some(ext) = &f.extension() {
                    if !self
                        .supported_formats()
                        .contains(&ext.to_string_lossy().to_lowercase().as_str())
                    {
                        return Err(io::Error::new(
                            io::ErrorKind::InvalidInput,
                            "File format not supported for image conversion",
                        ));
                    }
                } else {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidInput,
                        "Cannot infer extension from file name, please add an extension if this is an image",
                    ));
                }
                extension = f.extension().unwrap().to_string_lossy().to_lowercase();
            }
        };
        if self
            .image_converter
            .supported_formats()
            .contains(&extension.as_str())
        {
            self.image_converter.convert(input)
        } else if self
            .office_converter
            .supported_formats()
            .contains(&extension.as_str())
        {
            self.office_converter.convert(input)
        } else if self
            .markup_converter
            .supported_formats()
            .contains(&extension.as_str())
        {
            self.markup_converter.convert(input)
        } else if extension == "pdf" {
            // PDF -> PDF is a no-op
            match input.into() {
                types::ConversionInput::Binary(b) => Ok(b),
                types::ConversionInput::File(f) => {
                    let d = fs::read(f)?;
                    Ok(d)
                }
            }
        } else {
            self.text_converter.convert(input)
        }
    }
}

#[cfg(test)]
mod tests {
    use std::io::Write;

    use super::*;

    #[test]
    fn test_pdfitdown_converter_supported_formats() {
        let converter = PdfItDownConverter::default();
        let formats = converter.supported_formats();
        assert!(formats.contains(&"png"));
        assert!(formats.contains(&"jpg"));
        assert!(formats.contains(&"docx"));
        assert!(formats.contains(&"xlsx"));
        assert!(formats.contains(&"pptx"));
        assert!(formats.contains(&"html"));
        assert!(formats.contains(&"md"));
        assert!(formats.contains(&"txt"));
        assert!(formats.contains(&"rs"));
        assert!(formats.contains(&"json"));
        assert!(formats.contains(&"pdf"));
        assert!(!formats.contains(&"unknown"));
    }

    #[test]
    fn test_pdfitdown_converter_convert_image() {
        let png = crate::img::make_1x1_png(255, 0, 0, 255);
        let converter = PdfItDownConverter::default();
        let converted = converter.convert(png).expect("Should convert PNG to PDF");
        let kind = infer::get(&converted).expect("Should infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_pdfitdown_converter_convert_text() {
        let converter = PdfItDownConverter::default();
        let text = "Hello world\n";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".txt").unwrap();
        tmp.write_all(text.as_bytes()).unwrap();

        let converted = converter
            .convert(tmp.path().to_owned())
            .expect("Should convert text file to PDF");
        let kind = infer::get(&converted).expect("Should infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_pdfitdown_converter_convert_markdown() {
        let converter = PdfItDownConverter::default();
        let md = "# Hello\n\nWorld\n";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".md").unwrap();
        tmp.write_all(md.as_bytes()).unwrap();

        let converted = converter
            .convert(tmp.path().to_owned())
            .expect("Should convert Markdown file to PDF");
        let kind = infer::get(&converted).expect("Should infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_pdfitdown_converter_convert_pdf_noop() {
        let converter = PdfItDownConverter::default();
        let pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".pdf").unwrap();
        tmp.write_all(pdf).unwrap();

        let converted = converter
            .convert(tmp.path().to_owned())
            .expect("Should pass through PDF");
        assert_eq!(&converted, pdf.as_slice());
    }

    #[test]
    fn test_pdfitdown_converter_convert_unsupported() {
        let converter = PdfItDownConverter::default();
        let result = converter.convert(vec![0x00, 0x01, 0x02, 0x03]);
        assert!(result.is_err());
    }

    #[test]
    fn test_pdfitdown_converter_convert_to_file_no_overwrite_error() {
        let png = crate::img::make_1x1_png(255, 0, 0, 255);
        let mut tmp = tempfile::NamedTempFile::with_suffix(".png").unwrap();
        let out = tempfile::NamedTempFile::with_suffix(".pdf").unwrap();
        tmp.write_all(&png).unwrap();

        let converter = PdfItDownConverter::default();
        // First conversion succeeds
        converter
            .convert_to_file(tmp.path().to_owned(), out.path(), true)
            .expect("First conversion should succeed");

        // Second conversion with overwrite=false should fail
        let result = converter.convert_to_file(tmp.path().to_owned(), out.path(), false);
        assert!(result.is_err());
        let err = result.unwrap_err();
        assert_eq!(err.kind(), io::ErrorKind::AlreadyExists);
    }

    #[test]
    fn test_pdfitdown_converter_convert_directory_recursive() {
        let png = crate::img::make_1x1_png(255, 0, 0, 255);
        let md = "# Hello\n";
        let txt = "Hello world\n";

        let tmp_dir = tempfile::tempdir().unwrap();
        let sub_dir = tmp_dir.path().join("subdir");
        fs::create_dir(&sub_dir).unwrap();

        let mut tmp_1 = tempfile::NamedTempFile::with_suffix_in(".png", tmp_dir.path()).unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix_in(".md", &sub_dir).unwrap();
        let mut tmp_3 = tempfile::NamedTempFile::with_suffix_in(".txt", &sub_dir).unwrap();
        tmp_1.write_all(&png).unwrap();
        tmp_2.write_all(md.as_bytes()).unwrap();
        tmp_3.write_all(txt.as_bytes()).unwrap();

        let converter = PdfItDownConverter::default();
        converter
            .convert_directory(tmp_dir.path(), true, true)
            .expect("Should convert recursively");

        // Top-level file
        assert!(tmp_1.path().with_extension("pdf").exists());
        let converted = fs::read(tmp_1.path().with_extension("pdf")).expect("Should read file");
        let kind = infer::get(&converted).expect("Should infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");

        // Nested files
        assert!(tmp_2.path().with_extension("pdf").exists());
        let converted = fs::read(tmp_2.path().with_extension("pdf")).expect("Should read file");
        let kind = infer::get(&converted).expect("Should infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");

        assert!(tmp_3.path().with_extension("pdf").exists());
        let converted = fs::read(tmp_3.path().with_extension("pdf")).expect("Should read file");
        let kind = infer::get(&converted).expect("Should infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_pdfitdown_converter_convert_directory_non_recursive() {
        let png = crate::img::make_1x1_png(255, 0, 0, 255);
        let md = "# Hello\n";

        let tmp_dir = tempfile::tempdir().unwrap();
        let sub_dir = tmp_dir.path().join("subdir");
        fs::create_dir(&sub_dir).unwrap();

        let mut tmp_1 = tempfile::NamedTempFile::with_suffix_in(".png", tmp_dir.path()).unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix_in(".md", &sub_dir).unwrap();
        tmp_1.write_all(&png).unwrap();
        tmp_2.write_all(md.as_bytes()).unwrap();

        let converter = PdfItDownConverter::default();
        converter
            .convert_directory(tmp_dir.path(), true, false)
            .expect("Should convert non-recursively");

        // Top-level file should be converted
        assert!(tmp_1.path().with_extension("pdf").exists());

        // Nested file should NOT be converted
        assert!(!tmp_2.path().with_extension("pdf").exists());
    }

    #[test]
    fn test_pdfitdown_converter_convert_multiple_files() {
        let png = crate::img::make_1x1_png(255, 0, 0, 255);
        let md = "# Hello\n";

        let mut tmp_1 = tempfile::NamedTempFile::with_suffix(".png").unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix(".md").unwrap();
        tmp_1.write_all(&png).unwrap();
        tmp_2.write_all(md.as_bytes()).unwrap();

        let converter = PdfItDownConverter::default();
        converter
            .convert_multiple_files(
                vec![tmp_1.path().to_owned(), tmp_2.path().to_owned()],
                vec![
                    tmp_1.path().with_extension("pdf"),
                    tmp_2.path().with_extension("pdf"),
                ],
                true,
            )
            .expect("Should convert multiple files");

        for t in [&tmp_1, &tmp_2] {
            assert!(t.path().with_extension("pdf").exists());
            let converted = fs::read(t.path().with_extension("pdf")).expect("Should read file");
            let kind = infer::get(&converted).expect("Should infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }
}
