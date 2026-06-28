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
