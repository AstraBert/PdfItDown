use std::{fs, io, path::PathBuf};

#[cfg(feature = "rayon")]
use rayon::prelude::*;

#[derive(Debug, Clone)]
pub enum ConversionInput {
    Binary(Vec<u8>),
    File(PathBuf),
}

impl From<Vec<u8>> for ConversionInput {
    fn from(val: Vec<u8>) -> Self {
        ConversionInput::Binary(val)
    }
}

impl From<&[u8]> for ConversionInput {
    fn from(val: &[u8]) -> Self {
        ConversionInput::Binary(val.to_vec())
    }
}

impl From<String> for ConversionInput {
    fn from(val: String) -> Self {
        ConversionInput::File(PathBuf::from(val))
    }
}

impl From<PathBuf> for ConversionInput {
    fn from(val: PathBuf) -> Self {
        ConversionInput::File(val)
    }
}

impl From<&str> for ConversionInput {
    fn from(val: &str) -> Self {
        ConversionInput::File(PathBuf::from(val))
    }
}

pub trait Converter: Send + Sync {
    fn convert(&self, input: impl Into<ConversionInput> + Clone) -> io::Result<Vec<u8>>;
    /// Supported formats for conversion
    fn supported_formats(&self) -> &'static [&'static str];
    /// Apply the `convert` method to an input and save the PDF
    /// binary data to a file
    fn convert_to_file(
        &self,
        input: impl Into<ConversionInput> + Clone,
        output: impl Into<PathBuf> + Clone,
        overwrite: bool,
    ) -> io::Result<()> {
        let path = output.clone().into();
        if let Some(ext) = &path.extension()
            && ext.to_string_lossy() != "pdf"
        {
            return Err(io::Error::new(
                io::ErrorKind::Unsupported,
                "Only PDF files can be specified as output type of this operation",
            ));
        }
        if path.exists() && !overwrite {
            return Err(io::Error::new(
                io::ErrorKind::AlreadyExists,
                "Output file already exists and overwrite is set to False.",
            ));
        }
        let data = self.convert(input)?;
        std::fs::write(output.into(), data)
    }

    /// Convert multiple files to PDF.
    ///
    /// This function can be parallelized with the `rayon` feature.
    fn convert_multiple_files(
        &self,
        input: Vec<impl Into<ConversionInput> + Clone>,
        output: Vec<impl Into<PathBuf> + Clone>,
        overwrite: bool,
    ) -> io::Result<()> {
        if input.len() != output.len() {
            return Err(io::Error::other(
                "Number of inputs and outputs must be the same",
            ));
        }
        #[cfg(not(feature = "rayon"))]
        for (i, o) in input.iter().zip(output.iter()) {
            self.convert_to_file(i.to_owned(), o.to_owned(), overwrite)?;
        }

        #[cfg(feature = "rayon")]
        {
            let input: Vec<ConversionInput> = input.into_iter().map(Into::into).collect();
            let output: Vec<PathBuf> = output.into_iter().map(Into::into).collect();
            input
                .par_iter()
                .zip(output.par_iter())
                .try_for_each(|(i, o)| self.convert_to_file(i.clone(), o.clone(), overwrite))?;
        }

        Ok(())
    }

    /// Convert the files in a directory to PDF, optionally going through the directory recursively.
    ///
    /// This function can be parallelized with the `rayon` feature.
    fn convert_directory(
        &self,
        directory: impl Into<PathBuf>,
        overwrite: bool,
        recursive: bool,
    ) -> io::Result<()> {
        let mut inputs: Vec<PathBuf> = vec![];
        let mut outputs: Vec<PathBuf> = vec![];
        for entry in fs::read_dir(directory.into())? {
            let entry = entry?;
            let path = entry.path();
            if path.is_file() {
                inputs.push(path.clone());
                outputs.push(path.with_extension("pdf"));
            }
            if path.is_dir() && recursive {
                self.convert_directory(entry.path(), overwrite, recursive)?;
            }
        }
        self.convert_multiple_files(inputs, outputs, overwrite)?;

        Ok(())
    }
}
