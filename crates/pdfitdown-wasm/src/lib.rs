use pdfitdown::types::{ConversionInput, Converter};
use pdfitdown::{
    ImageConverter, MarkupConverter, OfficeConverter, PdfItDownConverter, TextConverter,
};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn convert(input: &[u8]) -> Result<Vec<u8>, JsError> {
    let converter = PdfItDownConverter::new();
    converter
        .convert(ConversionInput::Binary(input.to_vec()))
        .map_err(|e| JsError::new(&e.to_string()))
}

#[wasm_bindgen(js_name = convertImage)]
pub fn convert_image(input: &[u8]) -> Result<Vec<u8>, JsError> {
    let converter = ImageConverter::default();
    converter
        .convert(ConversionInput::Binary(input.to_vec()))
        .map_err(|e| JsError::new(&e.to_string()))
}

#[wasm_bindgen(js_name = convertMarkup)]
pub fn convert_markup(input: &[u8]) -> Result<Vec<u8>, JsError> {
    let converter = MarkupConverter::default();
    converter
        .convert(ConversionInput::Binary(input.to_vec()))
        .map_err(|e| JsError::new(&e.to_string()))
}

#[wasm_bindgen(js_name = convertOffice)]
pub fn convert_office(input: &[u8]) -> Result<Vec<u8>, JsError> {
    let converter = OfficeConverter::default();
    converter
        .convert(ConversionInput::Binary(input.to_vec()))
        .map_err(|e| JsError::new(&e.to_string()))
}

#[wasm_bindgen(js_name = convertText)]
pub fn convert_text(input: &[u8]) -> Result<Vec<u8>, JsError> {
    let converter = TextConverter::default();
    converter
        .convert(ConversionInput::Binary(input.to_vec()))
        .map_err(|e| JsError::new(&e.to_string()))
}
