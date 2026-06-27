use std::io;

use libreoffice_pure::{convert_bytes, sniff_format_from_bytes};

use crate::types::{ConversionInput, Converter};

#[derive(Debug, Clone, Copy)]
/// Struct implementing the converter trait for Office documents
pub struct OfficeConverter {}

impl Converter for OfficeConverter {
    fn supported_formats(&self) -> &'static [&'static str] {
        &[
            "docx", "xlsx", "pptx", "odt", "ods", "odp", "odg", "odf", "odb", "csv", "txt", "json",
        ]
    }

    fn convert(&self, input: impl Into<ConversionInput>) -> io::Result<Vec<u8>> {
        let data;
        match input.into() {
            ConversionInput::Binary(b) => {
                data = b;
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

        let format = sniff_format_from_bytes(&data);
        if let Some(form) = format {
            println!("{}", form);
            let pdf = convert_bytes(&data, &form, "pdf")
                .map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
            return Ok(pdf);
        }
        Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "Cannot determine the input format for the provided data",
        ))
    }
}
