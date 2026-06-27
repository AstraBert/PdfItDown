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
                let d = std::fs::read_to_string(&f)?;
                extension = f.extension().unwrap().to_string_lossy().to_string();
                data = d;
            }
        };
        let markdown = self.to_markdown(&data, &extension);
        self.markup_converter.convert(markdown.as_bytes())
    }
}
