use std::io;

use crate::types::{ConversionInput, Converter};

#[derive(Debug, Clone, Copy, Default)]
/// Struct implementing the converter trait for Office documents
pub struct OfficeConverter {}

impl OfficeConverter {
    fn to_format(self, extension: &str) -> Option<office2pdf::config::Format> {
        match extension {
            "docx" => Some(office2pdf::config::Format::Docx),
            "pptx" => Some(office2pdf::config::Format::Pptx),
            "xlsx" => Some(office2pdf::config::Format::Xlsx),
            _ => None,
        }
    }
}

impl Converter for OfficeConverter {
    fn supported_formats(&self) -> &'static [&'static str] {
        &["docx", "xlsx", "pptx"]
    }

    /// Convert office files to PDF (migth be unstable)
    fn convert(&self, input: impl Into<ConversionInput> + Clone) -> io::Result<Vec<u8>> {
        let data;
        match input.into() {
            ConversionInput::Binary(b) => {
                let kind = infer::get(&b);
                if let Some(k) = kind
                    && self
                        .supported_formats()
                        .contains(&k.extension().to_lowercase().as_str())
                {
                    data = b;
                } else {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidData,
                        "Inferred file type is not supported",
                    ));
                }
            }
            ConversionInput::File(f) => {
                if let Some(ext) = f.extension() {
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
                let d = std::fs::read(f)?;
                data = d;
            }
        };

        let format = infer::get(&data);
        if let Some(form) = format {
            let office_format = self.to_format(form.extension());
            if let Some(of) = office_format {
                let pdf = office2pdf::convert_bytes(
                    &data,
                    of,
                    &office2pdf::config::ConvertOptions::default(),
                )
                .map_err(|e| io::Error::other(e.to_string()))?;
                return Ok(pdf.pdf);
            }
            return Err(io::Error::other("Unsupported office file format"));
        }
        Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Cannot determine the input format for the provided data",
        ))
    }
}

#[cfg(test)]
mod tests {
    use std::io::Write;

    use super::*;

    /// Build a minimal valid DOCX file in memory.
    /// A DOCX is a ZIP archive containing [Content_Types].xml, _rels/.rels,
    /// word/_rels/document.xml.rels, and word/document.xml.
    fn make_minimal_docx() -> Vec<u8> {
        let mut buf = Vec::new();
        {
            let mut zip = zip::ZipWriter::new(std::io::Cursor::new(&mut buf));
            let options = zip::write::SimpleFileOptions::default()
                .compression_method(zip::CompressionMethod::Stored);

            zip.start_file("[Content_Types].xml", options).unwrap();
            zip.write_all(
                br#"<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"#,
            )
            .unwrap();

            zip.start_file("_rels/.rels", options).unwrap();
            zip.write_all(
                br#"<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"#,
            )
            .unwrap();

            zip.start_file("word/_rels/document.xml.rels", options)
                .unwrap();
            zip.write_all(
                br#"<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>"#,
            )
            .unwrap();

            zip.start_file("word/document.xml", options).unwrap();
            zip.write_all(
                br#"<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>Hello World</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>"#,
            )
            .unwrap();

            zip.finish().unwrap();
        }
        buf
    }

    #[test]
    fn test_office_converter_supported_formats() {
        let converter = OfficeConverter::default();
        assert_eq!(converter.supported_formats(), &["docx", "xlsx", "pptx"]);
    }

    #[test]
    fn test_office_converter_to_format() {
        let converter = OfficeConverter::default();
        assert_eq!(
            converter.to_format("docx"),
            Some(office2pdf::config::Format::Docx)
        );
        assert_eq!(
            converter.to_format("pptx"),
            Some(office2pdf::config::Format::Pptx)
        );
        assert_eq!(
            converter.to_format("xlsx"),
            Some(office2pdf::config::Format::Xlsx)
        );
        assert_eq!(converter.to_format("unknown"), None);
    }

    #[test]
    fn test_office_converter_convert_docx_bytes() {
        let docx = make_minimal_docx();
        let converter = OfficeConverter::default();
        let converted = converter
            .convert(docx)
            .expect("Should be able to convert DOCX bytes");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_office_converter_convert_unsupported_binary() {
        let converter = OfficeConverter::default();
        let result = converter.convert(vec![0x00, 0x01, 0x02, 0x03]);
        assert!(result.is_err());
    }

    #[test]
    fn test_office_converter_convert_unsupported_extension() {
        let converter = OfficeConverter::default();
        let result = converter.convert("test.png");
        assert!(result.is_err());
    }

    #[test]
    fn test_office_converter_convert_file_docx() {
        let docx = make_minimal_docx();
        let mut tmp = tempfile::NamedTempFile::with_suffix(".docx").unwrap();
        let other_file = tempfile::NamedTempFile::with_suffix(".pdf").unwrap();
        tmp.write_all(&docx).unwrap();

        let converter = OfficeConverter::default();
        converter
            .convert_to_file(tmp.path().to_owned(), other_file.path(), true)
            .expect("Should be able to convert DOCX file");
        let converted = std::fs::read(other_file.path()).expect("Should be able to read file");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_office_converter_convert_directory() {
        let docx_1 = make_minimal_docx();
        let docx_2 = make_minimal_docx();

        let tmp_dir = tempfile::tempdir().unwrap();
        let mut tmp_1 = tempfile::NamedTempFile::with_suffix_in(".docx", tmp_dir.path()).unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix_in(".DOCX", tmp_dir.path()).unwrap();
        tmp_1.write_all(&docx_1).unwrap();
        tmp_2.write_all(&docx_2).unwrap();

        let converter = OfficeConverter::default();
        converter
            .convert_directory(tmp_dir.path(), true, false)
            .expect("Should be able to convert files in directory");
        for t in [&tmp_1, &tmp_2] {
            assert!(t.path().with_extension("pdf").exists());
            let converted =
                std::fs::read(t.path().with_extension("pdf")).expect("Should be able to read file");
            let kind = infer::get(&converted).expect("Should be able to infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }

    #[test]
    fn test_office_converter_convert_multiple_files() {
        let docx_1 = make_minimal_docx();
        let docx_2 = make_minimal_docx();

        let mut tmp_1 = tempfile::NamedTempFile::with_suffix(".docx").unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix(".docx").unwrap();
        tmp_1.write_all(&docx_1).unwrap();
        tmp_2.write_all(&docx_2).unwrap();

        let converter = OfficeConverter::default();
        converter
            .convert_multiple_files(
                vec![tmp_1.path().to_owned(), tmp_2.path().to_owned()],
                vec![
                    tmp_1.path().with_extension("pdf"),
                    tmp_2.path().with_extension("pdf"),
                ],
                true,
            )
            .expect("Should be able to convert multiple files");
        for t in [&tmp_1, &tmp_2] {
            assert!(t.path().with_extension("pdf").exists());
            let converted =
                std::fs::read(t.path().with_extension("pdf")).expect("Should be able to read file");
            let kind = infer::get(&converted).expect("Should be able to infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }
}
