use std::{fs, io, path::PathBuf};

#[cfg(feature = "rayon")]
use rayon::prelude::*;

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
            && ext.to_string_lossy().to_string() != "pdf"
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
            return Err(io::Error::new(
                io::ErrorKind::Other,
                "Number of inputs and outputs must be the same",
            ));
        }
        #[cfg(not(feature = "rayon"))]
        for (i, o) in input.iter().zip(output.iter()) {
            self.convert_to_file(i.to_owned(), o.to_owned(), overwrite)?;
        }

        #[cfg(feature = "rayon")]
        input
            .par_iter()
            .zip(output.par_iter())
            .try_for_each(|(i, o)| self.convert_to_file(i.to_owned(), o.to_owned(), overwrite))?;

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
