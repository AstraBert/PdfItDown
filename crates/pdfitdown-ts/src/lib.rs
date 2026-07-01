#![deny(clippy::all)]

use napi::bindgen_prelude::Buffer;
use napi_derive::napi;
use pdfitdown::types::Converter;

#[napi]
pub struct PdfItDownConverter {
  inner: pdfitdown::PdfItDownConverter,
}

impl Default for PdfItDownConverter {
  fn default() -> Self {
    Self::new()
  }
}

#[napi]
impl PdfItDownConverter {
  #[napi(constructor)]
  pub fn new() -> Self {
    PdfItDownConverter {
      inner: pdfitdown::PdfItDownConverter::new(),
    }
  }

  #[napi]
  pub fn convert_bytes(&self, input: Buffer) -> napi::Result<Buffer> {
    let v: Vec<u8> = input.into();
    Ok(self.inner.convert(v)?.into())
  }

  #[napi]
  pub fn convert_file(
    &self,
    input_file: String,
    output_file: String,
    overwrite: bool,
  ) -> napi::Result<()> {
    self
      .inner
      .convert_to_file(input_file, &output_file, overwrite)?;
    Ok(())
  }

  #[napi]
  pub fn convert_multiple_files(
    &self,
    input_files: Vec<String>,
    output_files: Vec<String>,
    overwrite: bool,
  ) -> napi::Result<()> {
    self
      .inner
      .convert_multiple_files(input_files, output_files, overwrite)?;
    Ok(())
  }

  #[napi]
  pub fn convert_directory(
    &self,
    directory: String,
    overwrite: bool,
    recursive: bool,
  ) -> napi::Result<()> {
    self
      .inner
      .convert_directory(directory, overwrite, recursive)?;
    Ok(())
  }
}
