use std::io;

use crate::{
    markup::MarkupConverter,
    types::{ConversionInput, Converter},
};

#[derive(Debug, Clone, Copy, Default)]
pub struct TextConverter {
    markup_converter: MarkupConverter,
}

impl TextConverter {
    pub fn new() -> Self {
        TextConverter {
            markup_converter: MarkupConverter {},
        }
    }

    pub fn to_markdown(self, text: &str, extension: &str) -> String {
        if extension == "txt" {
            return text.to_string();
        }
        format!("```{}\n{}\n```\n", extension, text)
    }
}

impl Converter for TextConverter {
    fn supported_formats(&self) -> &'static [&'static str] {
        &[
            // Code
            "rs", "py", "js", "ts", "jsx", "tsx", "go", "c", "cpp", "h", "hpp", "java", "kt",
            "swift", "rb", "php", "cs", "scala", "hs", "lua", "r", "sh", "bash", "zsh", "fish",
            "ps1", "bat", "cmd", "css", "xml", // Data / Config
            "json", "yaml", "yml", "toml", // Docs
            "txt",  // Misc
            "csv", "tsv", "sql",
        ]
    }

    fn convert(&self, input: impl Into<ConversionInput> + Clone) -> io::Result<Vec<u8>> {
        #[allow(unused_variables)]
        let data;
        // treat binary data as text
        let mut extension = String::from("txt");
        match input.into() {
            ConversionInput::Binary(b) => {
                data = String::from_utf8_lossy(&b).to_string();
            }
            ConversionInput::File(f) => {
                if let Some(ext) = &f.extension() {
                    if !self
                        .supported_formats()
                        .contains(&ext.to_string_lossy().to_lowercase().as_str())
                    {
                        return Err(io::Error::new(
                            io::ErrorKind::InvalidInput,
                            "File format not supported for text conversion",
                        ));
                    }
                } else {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidInput,
                        "Cannot infer extension from file name, please add an extension if this is a text file",
                    ));
                }
                let d = std::fs::read_to_string(&f)?;
                extension = f.extension().unwrap().to_string_lossy().to_string();
                data = d;
            }
        };
        let markdown = self.to_markdown(&data, &extension);
        self.markup_converter.convert(markdown.as_bytes())
    }
}

#[cfg(test)]
mod tests {
    use std::io::Write;

    use super::*;

    #[test]
    fn test_text_converter_supported_formats() {
        let converter = TextConverter::default();
        let formats = converter.supported_formats();
        assert!(formats.contains(&"rs"));
        assert!(formats.contains(&"py"));
        assert!(formats.contains(&"js"));
        assert!(formats.contains(&"json"));
        assert!(formats.contains(&"yaml"));
        assert!(formats.contains(&"txt"));
        assert!(formats.contains(&"csv"));
        assert!(formats.contains(&"sql"));
        assert!(!formats.contains(&"png"));
    }

    #[test]
    fn test_text_converter_to_markdown_txt() {
        let converter = TextConverter::default();
        let text = "Hello world";
        let md = converter.to_markdown(text, "txt");
        assert_eq!(md, "Hello world");
    }

    #[test]
    fn test_text_converter_to_markdown_code() {
        let converter = TextConverter::default();
        let text = "fn main() {}";
        let md = converter.to_markdown(text, "rs");
        assert_eq!(md, "```rs\nfn main() {}\n```\n");
    }

    #[test]
    fn test_text_converter_convert_txt_bytes() {
        let converter = TextConverter::default();
        let text = "Hello world\n";
        let converted = converter
            .convert(text.as_bytes())
            .expect("Should convert text bytes to PDF");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_text_converter_convert_code_bytes() {
        let converter = TextConverter::default();
        let code = "fn main() {\n    println!(\"Hello\");\n}\n";
        let converted = converter
            .convert(code.as_bytes())
            .expect("Should convert code bytes to PDF");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_text_converter_convert_file_txt() {
        let text = "Hello world\n";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".txt").unwrap();
        let other_file = tempfile::NamedTempFile::with_suffix(".pdf").unwrap();
        tmp.write_all(text.as_bytes()).unwrap();

        let converter = TextConverter::default();
        converter
            .convert_to_file(tmp.path().to_owned(), other_file.path(), true)
            .expect("Should be able to convert text file");
        let converted = std::fs::read(other_file.path()).expect("Should be able to read file");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_text_converter_convert_file_rs() {
        let code = "fn main() {\n    println!(\"Hello\");\n}\n";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".rs").unwrap();
        let other_file = tempfile::NamedTempFile::with_suffix(".pdf").unwrap();
        tmp.write_all(code.as_bytes()).unwrap();

        let converter = TextConverter::default();
        converter
            .convert_to_file(tmp.path().to_owned(), other_file.path(), true)
            .expect("Should be able to convert Rust file");
        let converted = std::fs::read(other_file.path()).expect("Should be able to read file");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_text_converter_convert_unsupported_extension() {
        let text = "Hello world\n";
        let mut tmp = tempfile::NamedTempFile::with_suffix(".png").unwrap();
        tmp.write_all(text.as_bytes()).unwrap();

        let converter = TextConverter::default();
        let result = converter.convert(tmp.path().to_owned());
        assert!(result.is_err());
    }

    #[test]
    fn test_text_converter_convert_directory() {
        let code_1 = "fn main() {}\n";
        let code_2 = "print('hello')\n";
        let text_1 = "Hello world\n";

        let tmp_dir = tempfile::tempdir().unwrap();
        let mut tmp_1 = tempfile::NamedTempFile::with_suffix_in(".rs", tmp_dir.path()).unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix_in(".py", tmp_dir.path()).unwrap();
        let mut tmp_3 = tempfile::NamedTempFile::with_suffix_in(".TXT", tmp_dir.path()).unwrap();
        tmp_1.write_all(code_1.as_bytes()).unwrap();
        tmp_2.write_all(code_2.as_bytes()).unwrap();
        tmp_3.write_all(text_1.as_bytes()).unwrap();

        let converter = TextConverter::default();
        converter
            .convert_directory(tmp_dir.path(), true, false)
            .expect("Should be able to convert files in directory");
        for t in [&tmp_1, &tmp_2, &tmp_3] {
            assert!(t.path().with_extension("pdf").exists());
            let converted =
                std::fs::read(t.path().with_extension("pdf")).expect("Should be able to read file");
            let kind = infer::get(&converted).expect("Should be able to infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }

    #[test]
    fn test_text_converter_convert_multiple_files() {
        let code_1 = "fn main() {}\n";
        let code_2 = "print('hello')\n";

        let mut tmp_1 = tempfile::NamedTempFile::with_suffix(".rs").unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix(".py").unwrap();
        tmp_1.write_all(code_1.as_bytes()).unwrap();
        tmp_2.write_all(code_2.as_bytes()).unwrap();

        let converter = TextConverter::default();
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
                std::fs::read(t.path().with_extension("pdf")).expect("Should be able to read file");
            let kind = infer::get(&converted).expect("Should be able to infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }
}
