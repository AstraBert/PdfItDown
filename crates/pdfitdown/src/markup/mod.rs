use html_to_markdown_rs::convert;
use markdown2pdf::parse_into_bytes;
use regex::Regex;
use std::{
    fs,
    io::{self, ErrorKind},
    sync::OnceLock,
};

use crate::types::{ConversionInput, Converter};

static HTML_REGEX: OnceLock<Regex> = OnceLock::new();

fn html_regex() -> &'static Regex {
    HTML_REGEX.get_or_init(|| {
        Regex::new(r"(?i)<(html|head|body|div|span|p|a|img|table|ul|ol|li|h[1-6])[\s>]").unwrap()
    })
}

/// Struct implementing the Converter trait for markup languages (HTML, markdown)
#[derive(Debug, Clone, Copy, Default)]
pub struct MarkupConverter {}

impl MarkupConverter {
    pub fn convert_html_to_md(&self, html: &str) -> Result<String, io::Error> {
        let result =
            convert(html, None).map_err(|e| io::Error::new(ErrorKind::Other, e.to_string()))?;
        if let Some(content) = result.content {
            return Ok(content);
        }
        Err(io::Error::new(
            ErrorKind::Other,
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
        let data;
        match input.into() {
            ConversionInput::Binary(b) => data = String::from_utf8_lossy(&b).to_string(),
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
                data = fs::read_to_string(f)?;
            }
        }

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
        .map_err(|e| io::Error::new(ErrorKind::Other, e.to_string()))?;

        Ok(pdf_bytes)
    }
}
