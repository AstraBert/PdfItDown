use clap::Parser;
use pdfitdown::{PdfItDownConverter, types::Converter};

/// PdfItDown CLI: convert any file format to PDF
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

fn main() {
    let converter = PdfItDownConverter::default();
    let args = Args::parse();
    if args.inputfile.len() != args.outputfile.len() {
        eprintln!("\x1b[1;31mA different number of input and output files has been provided");
        std::process::exit(1);
    }
    if args.inputfile.len() > 0 {
        converter
            .convert_multiple_files(args.inputfile, args.outputfile, !args.no_overwrite)
            .map_or_else(
                |e| {
                    eprintln!("\x1b[1;31m{}", e.to_string());
                    std::process::exit(1)
                },
                |_| {},
            );
    } else if let Some(dir) = args.directory {
        converter
            .convert_directory(dir, !args.no_overwrite, args.recursive)
            .map_or_else(
                |e| {
                    eprintln!("\x1b[1;31m{}", e.to_string());
                    std::process::exit(1)
                },
                |_| {},
            );
    } else {
        eprintln!("\x1b[1;31mOne of --inputfile or --directory should be provided");
        std::process::exit(1);
    }

    println!("\x1b[1;32mConversion successful!🎉");
}
