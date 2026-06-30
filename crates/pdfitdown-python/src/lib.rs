use pyo3::prelude::*;
use std::fs;
use std::io;
use std::path::Path;

/// Collects all PDF files in `dir`, optionally descending into subdirectories.
pub fn collect_pdfs(dir: &Path, recursive: bool) -> io::Result<Vec<String>> {
    let mut pdfs = Vec::new();
    collect_pdfs_inner(dir, recursive, &mut pdfs)?;
    Ok(pdfs)
}

fn collect_pdfs_inner(dir: &Path, recursive: bool, pdfs: &mut Vec<String>) -> io::Result<()> {
    for entry in fs::read_dir(dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_dir() {
            if recursive {
                collect_pdfs_inner(&path, recursive, pdfs)?;
            }
        } else if is_pdf(&path) {
            pdfs.push(path.to_string_lossy().to_string());
        }
    }
    Ok(())
}

fn is_pdf(path: &Path) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| ext.eq_ignore_ascii_case("pdf"))
        .unwrap_or(false)
}

/// PdfItDown: Convert Anything to PDF
#[pymodule]
mod pdfitdown {
    #[pymodule_export]
    use super::pdfconversion;
    use pyo3::prelude::*;

    #[pymodule_export]
    use super::cli;

    #[pymodule_init]
    fn init(m: &Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
        let py = m.py();
        let sys_modules = py.import("sys")?.getattr("modules")?;
        sys_modules.set_item("pdfitdown.cli", m.getattr("cli")?)?;
        sys_modules.set_item("pdfitdown.pdfconversion", m.getattr("pdfconversion")?)?;
        Ok(())
    }
}

/// PDF conversion logic
#[pymodule]
mod pdfconversion {
    use std::path::PathBuf;

    use ::pdfitdown::PdfItDownConverter;
    use ::pdfitdown::types::Converter as ConverterTrait;
    use pyo3::prelude::*;

    #[pyclass]
    /// Converter class for handling file and directory conversions.
    struct Converter {
        inner: PdfItDownConverter,
    }

    #[pymethods]
    impl Converter {
        #[new]
        fn new() -> Self {
            Self {
                inner: PdfItDownConverter::new(),
            }
        }

        #[pyo3(signature = (file_path, output_path, overwrite = true))]
        /// Converts a file to PDF.
        ///
        /// Args:
        ///     file_path (str): The path to the input file.
        ///     output_path (str): The path where the converted PDF file will be saved.
        ///     title (str | None, optional): An optional title for the converted PDF file. Defaults to None.
        ///     overwrite (bool, optional): Whether to overwrite the output file if it already exists. Defaults to True.
        ///
        /// Returns:
        ///     str | None: The path to the converted file if successful, otherwise None.
        fn convert(
            &self,
            file_path: String,
            output_path: String,
            overwrite: bool,
        ) -> PyResult<String> {
            self.inner
                .convert_to_file(file_path, &output_path, overwrite)?;
            Ok(output_path)
        }

        #[pyo3(signature = (file_paths, output_paths = None, overwrite = true))]
        /// Converts multiple input files using the specified conversion logic.
        ///
        /// Args:
        ///     file_paths (list[str]): List of input file paths to be converted.
        ///     output_paths (list[str] | None, optional): List of output file paths. If None, output paths are determined automatically. Defaults to None.
        ///     overwrite (bool, optional): Whether to overwrite existing output files. Defaults to True.
        ///
        /// Returns:
        ///     list[str]: List of output file paths after conversion.
        fn multiple_convert(
            &self,
            file_paths: Vec<String>,
            output_paths: Option<Vec<String>>,
            overwrite: bool,
        ) -> PyResult<Vec<String>> {
            let out_paths = match output_paths {
                Some(p) => p,
                None => file_paths
                    .iter()
                    .map(|p| {
                        PathBuf::from(p)
                            .with_extension("pdf")
                            .to_string_lossy()
                            .to_string()
                    })
                    .collect(),
            };
            self.inner
                .convert_multiple_files(file_paths, out_paths.clone(), overwrite)?;
            Ok(out_paths)
        }

        #[pyo3(signature = (directory_path, overwrite = true, recursive = true))]
        /// Converts all files in the specified directory to the desired format.
        ///
        /// Args:
        ///     directory_path (str): The path to the directory containing files to convert.
        ///     overwrite (bool, optional): Whether to overwrite existing converted files. Defaults to True.
        ///     recursive (bool, optional): Whether to include files in subdirectories recursively. Defaults to True.
        ///
        /// Returns:
        ///     Result of the multiple file conversion process.
        fn convert_directory(
            &self,
            directory_path: String,
            overwrite: bool,
            recursive: bool,
        ) -> PyResult<Vec<String>> {
            use super::{Path, collect_pdfs};

            self.inner
                .convert_directory(&directory_path, overwrite, recursive)?;
            let pdfs = collect_pdfs(Path::new(&directory_path), recursive)?;

            Ok(pdfs)
        }
    }
}

/// CLI module
#[pymodule]
mod cli {
    use ::pdfitdown::{PdfItDownConverter, types::Converter};
    use clap::Parser;
    use pyo3::prelude::*;

    #[derive(Parser, Debug)]
    #[command(version = "4.0.0")]
    #[command(name = "pdfitdown")]
    #[command(about, long_about = None)]
    struct Args {
        #[arg(short, long)]
        /// Path to the input file(s) that need to be converted to PDF. Can be used multiple times.
        inputfile: Vec<String>,
        #[arg(short, long)]
        /// Path to the output PDF file(s). If more than one input file is provided, you should provide an equal number of output files.
        outputfile: Vec<String>,
        #[arg(short, long, default_value = None)]
        /// Directory whose files you want to bulk-convert to PDF. If `--inputfile` is also provided, this option will be ignored. Defaults to None.
        directory: Option<String>,
        #[arg(long, default_value_t = false)]
        /// Do not overwrite existing PDF files
        no_overwrite: bool,
        #[arg(long, default_value_t = false)]
        /// Recursively go through a directory when converting files to PDFs. Defaults to False, only considered when `--directory` is provided.
        recursive: bool,
    }

    #[pyfunction]
    fn cli_main(py: Python) -> PyResult<()> {
        let converter = PdfItDownConverter::default();
        let sys_argv: Vec<String> = py.import("sys")?.getattr("argv")?.extract()?;

        let args = Args::parse_from(sys_argv);
        if args.inputfile.len() != args.outputfile.len() {
            eprintln!("\x1b[1;31mA different number of input and output files has been provided");
            std::process::exit(1);
        }

        if !args.inputfile.is_empty() {
            converter
                .convert_multiple_files(args.inputfile, args.outputfile, !args.no_overwrite)
                .map_or_else(
                    |e| {
                        eprintln!("\x1b[1;31m{}", e);
                        std::process::exit(1)
                    },
                    |_| {},
                );
        } else if let Some(dir) = args.directory {
            converter
                .convert_directory(dir, !args.no_overwrite, args.recursive)
                .map_or_else(
                    |e| {
                        eprintln!("\x1b[1;31m{}", e);
                        std::process::exit(1)
                    },
                    |_| {},
                );
        } else {
            eprintln!("\x1b[1;31mOne of --inputfile or --directory should be provided");
            std::process::exit(1);
        }

        println!("\x1b[1;32mConversion successful!🎉");
        Ok(())
    }
}
