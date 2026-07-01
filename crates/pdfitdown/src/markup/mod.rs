use regex::Regex;
use std::sync::OnceLock;

pub static HTML_REGEX: OnceLock<Regex> = OnceLock::new();

pub fn html_regex() -> &'static Regex {
    HTML_REGEX.get_or_init(|| Regex::new(r"(?i)<(html|head|body)[\s>]").unwrap())
}

#[cfg(target_arch = "wasm32")]
mod inner {
    use std::{
        collections::BTreeMap,
        fs,
        io::{self},
    };

    use crate::types::{ConversionInput, Converter};

    use super::*;
    use printpdf::{GeneratePdfOptions, PdfDocument, PdfSaveOptions};

    /// Struct implementing the Converter trait for markup languages (HTML, markdown)
    #[derive(Debug, Clone, Copy, Default)]
    pub struct MarkupConverter {}

    impl MarkupConverter {
        pub fn convert_md_to_html(&self, md: &str) -> String {
            markdown::to_html(md)
        }
    }

    impl Converter for MarkupConverter {
        fn supported_formats(&self) -> &'static [&'static str] {
            &["html", "md", "markdown", "htm"]
        }

        /// Convert markup data to PDF
        fn convert(&self, input: impl Into<ConversionInput> + Clone) -> io::Result<Vec<u8>> {
            let data = match input.into() {
                ConversionInput::Binary(b) => String::from_utf8_lossy(&b).to_string(),
                ConversionInput::File(f) => {
                    if let Some(ext) = f.extension() {
                        if !self
                            .supported_formats()
                            .contains(&ext.to_string_lossy().to_lowercase().as_str())
                        {
                            return Err(io::Error::new(
                                io::ErrorKind::InvalidInput,
                                "File format not supported for markup conversion",
                            ));
                        }
                    } else {
                        return Err(io::Error::new(
                            io::ErrorKind::InvalidInput,
                            "Cannot infer extension from file name, please add an extension if this is a markup file",
                        ));
                    }
                    fs::read_to_string(f)?
                }
            };

            let to_convert = if !html_regex().is_match(&data) {
                let int = self.convert_md_to_html(&data);
                format!(
                    concat!(
                        "<!DOCTYPE html><html><head><style>",
                        "* {{ box-sizing: border-box; }}",
                        "html, body {{ width: 100%; margin: 0; padding: 0; display: block; }}",
                        "body {{ font-family: \"Helvetica\", sans-serif; }}",
                        "code {{ font-family: \"Courier\", monospace; }}",
                        "</style></head><body>{}</body></html>"
                    ),
                    int
                )
            } else {
                let style = "<style>body { font-family: \"Helvetica\", sans-serif; } code { font-family: \"Courier\", monospace; }</style>";
                if let Some(pos) = data.find("</head>") {
                    let mut s = data.clone();
                    s.insert_str(pos, style);
                    s
                } else {
                    // no <head> tag, just prepend
                    format!("{}{}", style, data)
                }
            };

            // On wasm there are no system fonts, so we must seed the font pool with
            // full TTF bytes that have intact NAME tables (required by FcParseFontBytes
            // for family-name resolution). The printpdf subset fonts lack a NAME table
            // and cannot be registered — using them yields an empty font cache and a
            // blank PDF. We bundle the full fonts via include_bytes! instead.
            let mut fonts: BTreeMap<String, printpdf::Base64OrRaw> = BTreeMap::new();
            macro_rules! embed_font {
                ($name:expr, $path:expr) => {
                    fonts.insert(
                        $name.to_string(),
                        printpdf::Base64OrRaw::Raw(
                            include_bytes!(concat!("../../assets/fonts/", $path)).to_vec(),
                        ),
                    );
                };
            }
            embed_font!("Helvetica", "Helvetica.ttf");
            embed_font!("Helvetica-Bold", "Helvetica-Bold.ttf");
            embed_font!("Helvetica-Oblique", "Helvetica-Oblique.ttf");
            embed_font!("Helvetica-BoldOblique", "Helvetica-BoldOblique.ttf");
            embed_font!("Times-Roman", "Times.ttf");
            embed_font!("Times-Bold", "Times-Bold.ttf");
            embed_font!("Times-Oblique", "Times-Oblique.ttf");
            embed_font!("Times-BoldOblique", "Times-BoldOblique.ttf");
            embed_font!("Courier", "Courier.ttf");
            embed_font!("Courier-Bold", "Courier-Bold.ttf");
            embed_font!("Courier-Oblique", "Courier-Oblique.ttf");
            embed_font!("Courier-BoldOblique", "Courier-BoldOblique.ttf");

            let images = BTreeMap::new();
            let options = GeneratePdfOptions::default();
            let mut warnings = Vec::new();

            web_sys::console::log_1(&format!("{}", to_convert).into());

            let doc = PdfDocument::from_html(&to_convert, &images, &fonts, &options, &mut warnings)
                .map_err(|e| io::Error::other(e.to_string()))?;

            if !warnings.is_empty() {
                let errors: Vec<_> = warnings
                    .iter()
                    .filter(|w| w.severity >= printpdf::PdfParseErrorSeverity::Warning)
                    .map(|w| w.msg.clone())
                    .collect();
                if !errors.is_empty() {
                    return Err(io::Error::other(errors.join("; ")));
                }
            }

            let pdf_bytes = doc.save(&PdfSaveOptions::default(), &mut warnings);

            if !warnings.is_empty() {
                let errors: Vec<_> = warnings
                    .iter()
                    .filter(|w| w.severity >= printpdf::PdfParseErrorSeverity::Warning)
                    .map(|w| w.msg.clone())
                    .collect();
                if !errors.is_empty() {
                    return Err(io::Error::other(errors.join("; ")));
                }
            }

            Ok(pdf_bytes)
        }
    }
}

#[cfg(not(target_arch = "wasm32"))]
mod inner {
    use super::*;
    use html_to_markdown_rs::convert;
    use markdown2pdf::parse_into_bytes;

    use std::{
        fs,
        io::{self},
    };

    use crate::types::{ConversionInput, Converter};

    /// Struct implementing the Converter trait for markup languages (HTML, markdown)
    #[derive(Debug, Clone, Copy, Default)]
    pub struct MarkupConverter {}

    impl MarkupConverter {
        pub fn convert_html_to_md(&self, html: &str) -> Result<String, io::Error> {
            let result = convert(html, None).map_err(|e| io::Error::other(e.to_string()))?;
            if let Some(content) = result.content {
                return Ok(content);
            }
            Err(io::Error::other(
                "No HTML -> Markdown converted content was produced",
            ))
        }
    }

    impl Converter for MarkupConverter {
        fn supported_formats(&self) -> &'static [&'static str] {
            &["html", "md", "markdown", "htm"]
        }

        /// Convert markup data to PDF
        fn convert(&self, input: impl Into<ConversionInput> + Clone) -> io::Result<Vec<u8>> {
            let data = match input.into() {
                ConversionInput::Binary(b) => String::from_utf8_lossy(&b).to_string(),
                ConversionInput::File(f) => {
                    if let Some(ext) = f.extension() {
                        if !self
                            .supported_formats()
                            .contains(&ext.to_string_lossy().to_lowercase().as_str())
                        {
                            return Err(io::Error::new(
                                io::ErrorKind::InvalidInput,
                                "File format not supported for markup conversion",
                            ));
                        }
                    } else {
                        return Err(io::Error::new(
                            io::ErrorKind::InvalidInput,
                            "Cannot infer extension from file name, please add an extension if this is a markup file",
                        ));
                    }
                    fs::read_to_string(f)?
                }
            };

            let to_convert = if html_regex().is_match(&data) {
                self.convert_html_to_md(&data)?
            } else {
                data
            };

            let pdf_bytes = parse_into_bytes(
                to_convert,
                markdown2pdf::config::ConfigSource::Default,
                None,
            )
            .map_err(|e| io::Error::other(e.to_string()))?;

            Ok(pdf_bytes)
        }
    }
}

pub use inner::MarkupConverter;

#[cfg(test)]
mod tests {
    use crate::types::Converter;
    use std::fs;
    use std::io::Write;

    use super::*;

    #[test]
    fn test_markup_converter_supported_formats() {
        let converter = MarkupConverter::default();
        assert_eq!(
            converter.supported_formats(),
            &["html", "md", "markdown", "htm"]
        );
    }

    #[test]
    #[cfg(target_arch = "wasm32")]
    fn test_markup_converter_convert_md_to_html() {
        let converter = MarkupConverter::default();
        let md = "# Hello\nWorld";
        let html = converter.convert_md_to_html(md);
        assert!(html.contains("<h1>Hello</h1>"));
        assert!(html.contains("World"));
    }

    #[test]
    #[cfg(not(target_arch = "wasm32"))]
    fn test_markup_converter_convert_html_to_md() {
        let converter = MarkupConverter::default();
        let md = "<h1>Hello</h1>\n<p>World</p>";
        let html = converter
            .convert_html_to_md(md)
            .expect("Should be able to convert html to md");
        assert!(html.contains("# Hello"));
        assert!(html.contains("World"));
    }

    #[test]
    fn test_markup_converter_convert_markdown_bytes() {
        let converter = MarkupConverter::default();
        let md = "# Hello\n\nThis is a test.\n";
        let converted = converter
            .convert(md.as_bytes())
            .expect("Should convert Markdown bytes to PDF");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_markup_converter_convert_html_bytes() {
        let converter = MarkupConverter::default();
        let html = "<html><body><h1>Hello</h1><p>World</p></body></html>";
        let converted = converter
            .convert(html.as_bytes())
            .expect("Should convert HTML bytes to PDF");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_markup_converter_convert_file_md() {
        let md = "# Test\n\nHello world\n";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".md").unwrap();
        let other_file = tempfile::NamedTempFile::with_suffix(".pdf").unwrap();
        tmp.write_all(md.as_bytes()).unwrap();

        let converter = MarkupConverter::default();
        converter
            .convert_to_file(tmp.path().to_owned(), other_file.path(), true)
            .expect("Should be able to convert Markdown file");
        let converted = fs::read(other_file.path()).expect("Should be able to read file");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_markup_converter_convert_file_html() {
        let html = "<html><body><h1>Test</h1></body></html>";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".html").unwrap();
        let other_file = tempfile::NamedTempFile::with_suffix(".pdf").unwrap();
        tmp.write_all(html.as_bytes()).unwrap();

        let converter = MarkupConverter::default();
        converter
            .convert_to_file(tmp.path().to_owned(), other_file.path(), true)
            .expect("Should be able to convert HTML file");
        let converted = fs::read(other_file.path()).expect("Should be able to read file");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_markup_converter_convert_unsupported_extension() {
        let md = "# Test\n";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".png").unwrap();
        tmp.write_all(md.as_bytes()).unwrap();

        let converter = MarkupConverter::default();
        let result = converter.convert(tmp.path().to_owned());
        assert!(result.is_err());
    }

    #[test]
    fn test_markup_converter_convert_directory() {
        let md_1 = "# File 1\n";
        let md_2 = "# File 2\n";
        let html_1 = "<html><body><h1>HTML File</h1></body></html>";

        let tmp_dir = tempfile::tempdir().unwrap();
        let mut tmp_1 = tempfile::NamedTempFile::with_suffix_in(".MD", tmp_dir.path()).unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix_in(".md", tmp_dir.path()).unwrap();
        let mut tmp_3 = tempfile::NamedTempFile::with_suffix_in(".html", tmp_dir.path()).unwrap();
        tmp_1.write_all(md_1.as_bytes()).unwrap();
        tmp_2.write_all(md_2.as_bytes()).unwrap();
        tmp_3.write_all(html_1.as_bytes()).unwrap();

        let converter = MarkupConverter::default();
        converter
            .convert_directory(tmp_dir.path(), true, false)
            .expect("Should be able to convert files in directory");
        for t in [&tmp_1, &tmp_2, &tmp_3] {
            assert!(t.path().with_extension("pdf").exists());
            let converted =
                fs::read(t.path().with_extension("pdf")).expect("Should be able to read file");
            let kind = infer::get(&converted).expect("Should be able to infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }

    #[test]
    fn test_markup_converter_convert_multiple_files() {
        let md_1 = "# File 1\n";
        let md_2 = "# File 2\n";

        let mut tmp_1 = tempfile::NamedTempFile::with_suffix(".md").unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix(".md").unwrap();
        tmp_1.write_all(md_1.as_bytes()).unwrap();
        tmp_2.write_all(md_2.as_bytes()).unwrap();

        let converter = MarkupConverter::default();
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
                fs::read(t.path().with_extension("pdf")).expect("Should be able to read file");
            let kind = infer::get(&converted).expect("Should be able to infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }
}
