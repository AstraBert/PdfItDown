use std::{io, path::PathBuf};

#[derive(Debug, Clone)]
pub enum ConversionInput {
    Binary(Vec<u8>),
    File(PathBuf),
}

impl Into<ConversionInput> for Vec<u8> {
    fn into(self) -> ConversionInput {
        ConversionInput::Binary(self)
    }
}

impl Into<ConversionInput> for &[u8] {
    fn into(self) -> ConversionInput {
        ConversionInput::Binary(self.to_vec())
    }
}

impl Into<ConversionInput> for String {
    fn into(self) -> ConversionInput {
        ConversionInput::File(PathBuf::from(self))
    }
}

impl Into<ConversionInput> for PathBuf {
    fn into(self) -> ConversionInput {
        ConversionInput::File(self)
    }
}

impl Into<ConversionInput> for &str {
    fn into(self) -> ConversionInput {
        ConversionInput::File(PathBuf::from(self))
    }
}

pub trait Converter {
    fn convert(&self, input: impl Into<ConversionInput>) -> io::Result<Vec<u8>>;
    /// Supported formats for conversion
    fn supported_formats(&self) -> &'static [&'static str];
    /// Apply the `convert` method to an input and save the PDF
    /// binary data to a file
    fn convert_to_file(
        &self,
        input: impl Into<ConversionInput>,
        output: impl Into<PathBuf>,
    ) -> io::Result<()> {
        let data = self.convert(input)?;
        std::fs::write(output.into(), data)
    }
}
