use flate2::Compression;
use flate2::write::ZlibEncoder;
use image::{DynamicImage, GenericImageView};
use std::io::{self, Write};

use crate::types::{ConversionInput, Converter};

#[derive(Debug, Clone, Copy, Default)]
/// Struct implementing the Converter trait for images
pub struct ImageConverter {}

impl Converter for ImageConverter {
    fn supported_formats(&self) -> &'static [&'static str] {
        &["png", "jpg", "jpeg", "avif", "tiff", "webp"]
    }
    /// Convert an image to PDF bytes
    fn convert(&self, input: impl Into<ConversionInput> + Clone) -> io::Result<Vec<u8>> {
        let data;
        match input.into() {
            ConversionInput::Binary(b) => {
                let kind = infer::get(&b);
                if let Some(k) = kind
                    && self.supported_formats().contains(&k.extension())
                {
                    data = b;
                } else {
                    return Err(io::Error::new(
                        io::ErrorKind::InvalidData,
                        "Inferred file type is not supported",
                    ));
                }
            }
            ConversionInput::File(f) => {
                if let Some(ext) = f.extension() {
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
                let d = std::fs::read(f)?;
                data = d;
            }
        };

        let img = image::load_from_memory(&data).map_err(|e| io::Error::other(e.to_string()))?;

        let (width, height) = img.dimensions();

        let (rgb_img, mask_img) = separate_rgb_and_alpha(img);

        let mut encoder = ZlibEncoder::new(Vec::new(), Compression::best());
        encoder.write_all(&rgb_img)?;
        let rgb_data = encoder.finish()?;

        let mut encoder = ZlibEncoder::new(Vec::new(), Compression::best());
        encoder.write_all(&mask_img)?;
        let mask_data = encoder.finish()?;

        let mut pdf_data = Vec::new();

        writeln!(pdf_data, "%PDF-1.4")?;

        let image_object_id = 2;
        let image_object_pos = pdf_data.len();
        writeln!(
            pdf_data,
            "{} 0 obj\n<< /Type /XObject /Subtype /Image /Width {} /Height {} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {} /SMask {} 0 R >>",
            image_object_id,
            width,
            height,
            rgb_data.len(),
            image_object_id + 1
        )?;
        writeln!(pdf_data, "stream")?;
        pdf_data.extend(&rgb_data);
        writeln!(pdf_data, "endstream\nendobj")?;

        let mask_object_id = image_object_id + 1;
        let mask_object_pos = pdf_data.len();
        writeln!(
            pdf_data,
            "{} 0 obj\n<< /Type /XObject /Subtype /Image /Width {} /Height {} /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode /Length {} >>",
            mask_object_id,
            width,
            height,
            mask_data.len()
        )?;
        writeln!(pdf_data, "stream")?;
        pdf_data.extend(&mask_data);
        writeln!(pdf_data, "endstream\nendobj")?;

        let content_stream_object_id = 5;
        let content_stream_pos = pdf_data.len();
        let content = format!(
            "q\n{} 0 0 {} 0 0 cm\n/Im{} Do\nQ",
            width, height, image_object_id
        );
        writeln!(
            pdf_data,
            "{} 0 obj\n<< /Length {} >>",
            content_stream_object_id,
            content.len()
        )?;
        writeln!(pdf_data, "stream\n{}\nendstream\nendobj", content)?;

        let page_object_id = 4;
        let page_object_pos = pdf_data.len();
        writeln!(
            pdf_data,
            "{} 0 obj\n<< /Type /Page /Parent 1 0 R /MediaBox [0 0 {} {}] /Contents {} 0 R /Resources << /XObject << /Im{} {} 0 R >> >> >>",
            page_object_id,
            width,
            height,
            content_stream_object_id,
            image_object_id,
            image_object_id
        )?;
        writeln!(pdf_data, "endobj")?;

        let pages_object_pos = pdf_data.len();
        writeln!(
            pdf_data,
            "1 0 obj\n<< /Type /Pages /Kids [ {} 0 R ] /Count 1 >>",
            page_object_id
        )?;
        writeln!(pdf_data, "endobj")?;

        let catalog_object_pos = pdf_data.len();
        writeln!(pdf_data, "6 0 obj\n<< /Type /Catalog /Pages 1 0 R >>")?;
        writeln!(pdf_data, "endobj")?;

        let xref_start = pdf_data.len();
        writeln!(pdf_data, "xref")?;
        writeln!(pdf_data, "0 7")?;
        writeln!(pdf_data, "0000000000 65535 f ")?;
        writeln!(pdf_data, "{:010} 00000 n ", pages_object_pos)?;
        writeln!(pdf_data, "{:010} 00000 n ", image_object_pos)?;
        writeln!(pdf_data, "{:010} 00000 n ", mask_object_pos)?;
        writeln!(pdf_data, "{:010} 00000 n ", page_object_pos)?;
        writeln!(pdf_data, "{:010} 00000 n ", content_stream_pos)?;
        writeln!(pdf_data, "{:010} 00000 n ", catalog_object_pos)?;

        writeln!(pdf_data, "trailer\n<< /Size 7 /Root 6 0 R >>")?;
        writeln!(pdf_data, "startxref\n{}", xref_start)?;
        writeln!(pdf_data, "%%EOF")?;

        Ok(pdf_data)
    }
}

/// Separates the RGB and alpha channels of an image.
fn separate_rgb_and_alpha(img: DynamicImage) -> (Vec<u8>, Vec<u8>) {
    let rgba = img.to_rgba8();
    let mut rgb = Vec::with_capacity(rgba.len() / 4 * 3);
    let mut alpha = Vec::with_capacity(rgba.len() / 4);

    for pixel in rgba.pixels() {
        rgb.push(pixel[0]);
        rgb.push(pixel[1]);
        rgb.push(pixel[2]);
        alpha.push(pixel[3]);
    }

    (rgb, alpha)
}

#[cfg(test)]
pub(crate) fn make_1x1_png(r: u8, g: u8, b: u8, a: u8) -> Vec<u8> {
    // PNG signature
    let mut out = vec![0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];

    // IHDR chunk: 1x1, 8-bit RGBA
    write_chunk(
        &mut out,
        b"IHDR",
        &[
            0, 0, 0, 1, // width = 1
            0, 0, 0, 1, // height = 1
            8, // bit depth
            6, // color type = RGBA
            0, 0, 0, // compression, filter, interlace
        ],
    );

    // IDAT chunk: zlib-wrap the pixel (filter byte 0x00 + RGBA)
    let raw = [0x00, r, g, b, a];
    write_chunk(&mut out, b"IDAT", &zlib_deflate(&raw));

    // IEND chunk
    write_chunk(&mut out, b"IEND", &[]);

    out
}

#[cfg(test)]
#[allow(dead_code)]
fn write_chunk(out: &mut Vec<u8>, name: &[u8; 4], data: &[u8]) {
    let len = data.len() as u32;
    out.extend_from_slice(&len.to_be_bytes());
    out.extend_from_slice(name);
    out.extend_from_slice(data);
    let crc = crc32(&[name.as_slice(), data].concat());
    out.extend_from_slice(&crc.to_be_bytes());
}

#[cfg(test)]
#[allow(dead_code)]
fn crc32(data: &[u8]) -> u32 {
    let mut crc = 0xFFFF_FFFFu32;
    for &byte in data {
        crc ^= byte as u32;
        for _ in 0..8 {
            if crc & 1 != 0 {
                crc = (crc >> 1) ^ 0xEDB8_8320;
            } else {
                crc >>= 1;
            }
        }
    }
    !crc
}

#[cfg(test)]
#[allow(dead_code)]
fn zlib_deflate(data: &[u8]) -> Vec<u8> {
    // zlib header (deflate, default compression)
    let mut out = vec![0x78, 0x01];

    // Non-compressed deflate block (BTYPE=00)
    let len = data.len() as u16;
    out.push(0x01); // BFINAL=1, BTYPE=00
    out.extend_from_slice(&len.to_le_bytes());
    out.extend_from_slice(&(!len).to_le_bytes());
    out.extend_from_slice(data);

    // Adler-32 checksum
    let (mut s1, mut s2) = (1u32, 0u32);
    for &b in data {
        s1 = (s1 + b as u32) % 65521;
        s2 = (s2 + s1) % 65521;
    }
    out.extend_from_slice(&((s2 << 16) | s1).to_be_bytes());

    out
}

#[cfg(test)]
mod tests {
    use std::fs;

    use super::*;

    #[test]
    fn test_image_converter_supported_type() {
        let converter = ImageConverter::default();
        assert_eq!(
            converter.supported_formats(),
            &["png", "jpg", "jpeg", "avif", "tiff", "webp"]
        )
    }

    #[test]
    fn test_image_converter_convert() {
        let png = make_1x1_png(255, 0, 0, 255);

        let converter = ImageConverter::default();
        let converted = converter
            .convert(png)
            .expect("Should be able to convert PNG image");
        let kind = infer::get(&converted).expect("Should be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_image_converter_convert_unsupported() {
        let png = make_1x1_png(255, 0, 0, 255);

        let converter = ImageConverter::default();
        let converted = converter
            .convert(png)
            .expect("Should be able to convert PNG image");
        let result = converter.convert(converted);
        assert!(result.is_err());
    }

    #[test]
    fn test_image_converter_convert_file() {
        let png = make_1x1_png(255, 0, 0, 255);
        let mut tmp = tempfile::NamedTempFile::with_suffix(".png").unwrap();
        let other_file = tempfile::NamedTempFile::with_suffix(".pdf").unwrap();
        tmp.write_all(&png).unwrap();

        let converter = ImageConverter::default();
        converter
            .convert_to_file(tmp.path().to_owned(), other_file.path(), true)
            .expect("Should be able to convert PNG image");
        let converted = fs::read(other_file.path()).expect("Should be able to read file");
        let kind = infer::get(&converted).expect("Shoule be able to infer kind");
        assert_eq!(kind.mime_type(), "application/pdf");
    }

    #[test]
    fn test_image_converter_convert_directory() {
        let png = make_1x1_png(255, 0, 0, 255);
        let png_1 = make_1x1_png(128, 0, 0, 255);
        let png_2 = make_1x1_png(213, 0, 0, 255);

        let tmp_dir = tempfile::tempdir().unwrap();
        let mut tmp = tempfile::NamedTempFile::with_suffix_in(".png", tmp_dir.path()).unwrap();
        let mut tmp_1 = tempfile::NamedTempFile::with_suffix_in(".png", tmp_dir.path()).unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix_in(".png", tmp_dir.path()).unwrap();
        tmp.write_all(&png).unwrap();
        tmp_1.write_all(&png_1).unwrap();
        tmp_2.write_all(&png_2).unwrap();

        let converter = ImageConverter::default();
        converter
            .convert_directory(tmp_dir.path(), true, false)
            .expect("Should be able to convert files in directory");
        for t in [&tmp, &tmp_1, &tmp_2] {
            assert!(t.path().with_extension("pdf").exists());
            let converted =
                fs::read(t.path().with_extension("pdf")).expect("Should be able to read file");
            let kind = infer::get(&converted).expect("Shoule be able to infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }

    #[test]
    fn test_image_converter_convert_files() {
        let png = make_1x1_png(255, 0, 0, 255);
        let png_1 = make_1x1_png(128, 0, 0, 255);
        let png_2 = make_1x1_png(213, 0, 0, 255);

        let mut tmp = tempfile::NamedTempFile::with_suffix(".PNG").unwrap();
        let mut tmp_1 = tempfile::NamedTempFile::with_suffix(".png").unwrap();
        let mut tmp_2 = tempfile::NamedTempFile::with_suffix(".png").unwrap();
        tmp.write_all(&png).unwrap();
        tmp_1.write_all(&png_1).unwrap();
        tmp_2.write_all(&png_2).unwrap();

        let converter = ImageConverter::default();
        converter
            .convert_multiple_files(
                vec![
                    tmp.path().to_owned(),
                    tmp_1.path().to_owned(),
                    tmp_2.path().to_owned(),
                ],
                vec![
                    tmp.path().with_extension("pdf"),
                    tmp_1.path().with_extension("pdf"),
                    tmp_2.path().with_extension("pdf"),
                ],
                true,
            )
            .expect("Should be able to convert files in directory");
        for t in [&tmp, &tmp_1, &tmp_2] {
            assert!(t.path().with_extension("pdf").exists());
            let converted =
                fs::read(t.path().with_extension("pdf")).expect("Should be able to read file");
            let kind = infer::get(&converted).expect("Shoule be able to infer kind");
            assert_eq!(kind.mime_type(), "application/pdf");
        }
    }
}
