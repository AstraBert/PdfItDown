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
                        .contains(&ext.to_string_lossy().to_string().as_str())
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
                .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
                return Ok(pdf.pdf);
            }
            return Err(io::Error::new(
                io::ErrorKind::Other,
                "Unsupported office file format",
            ));
        }
        Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Cannot determine the input format for the provided data",
        ))
    }
}
