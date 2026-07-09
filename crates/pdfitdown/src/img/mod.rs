use flate2::Compression;
use flate2::write::ZlibEncoder;
use image::{GenericImageView, ImageFormat};
use resvg::tiny_skia::Pixmap;
use resvg::usvg::{Options, Tree};
use std::io::{self, Write};

use crate::types::{ConversionInput, Converter};

#[derive(Debug, Clone, Copy, Default)]
/// Struct implementing the Converter trait for images
pub struct ImageConverter {}

// Separates RGB and alpha channels from raw RGBA8 bytes.
/// Used by the `resvg` SVG path where we always have RGBA output.
fn separate_rgb_and_alpha_from_rgba(rgba: &[u8]) -> (Vec<u8>, Vec<u8>) {
    let mut rgb = Vec::with_capacity(rgba.len() / 4 * 3);
    let mut alpha = Vec::with_capacity(rgba.len() / 4);

    for px in rgba.chunks_exact(4) {
        rgb.push(px[0]);
        rgb.push(px[1]);
        rgb.push(px[2]);
        alpha.push(px[3]);
    }

    (rgb, alpha)
}

/// Zlib-compress a byte slice at a speed/size tradeoff tuned for PDF
/// embedding. Level 3 is ~3× faster than the zlib default (level 6) on
/// photographic data and only ≈3% larger; deflate dominates end-to-end
/// time for any lossily-compressed input (JPEG-except-passthrough, WebP)
/// where the pixel stream is high-entropy.
fn deflate(data: &[u8]) -> io::Result<Vec<u8>> {
    let mut encoder = ZlibEncoder::new(Vec::with_capacity(data.len() / 4), Compression::new(3));
    encoder.write_all(data)?;
    encoder.finish()
}

/// The channel layout of the raster we're going to embed.
enum PixelData {
    /// Interleaved RGB, no alpha. Emitted as a single `/DeviceRGB` XObject.
    Rgb(Vec<u8>),
    /// De-interleaved RGB + 8-bit alpha mask. Emitted as an image XObject
    /// with a separate `/SMask` grayscale XObject.
    RgbWithAlpha { rgb: Vec<u8>, alpha: Vec<u8> },
}

/// PDF's default coordinate system is 150 points per inch. Images with no
/// embedded DPI metadata are assumed to be at this resolution, matching
/// ImageMagick's default behavior when converting images to PDF.
const DEFAULT_IMAGE_DPI: f32 = 150.0;

/// Read the pixel-density (DPI) metadata embedded in an image, if any.
///
/// This mirrors ImageMagick's behavior of sizing the resulting PDF page in
/// points based on the image's physical resolution rather than its pixel
/// dimensions.
///
/// Returns `(dpi_x, dpi_y)` in dots-per-inch, or `None` when the image has
/// no density metadata or the format doesn't carry it. Only PNG and JPEG
/// are inspected; other raster formats fall back to `DEFAULT_IMAGE_DPI`.
fn read_image_dpi(data: &[u8]) -> Option<(f32, f32)> {
    let format = image::guess_format(data).ok()?;
    match format {
        ImageFormat::Png => read_png_dpi(data),
        ImageFormat::Jpeg => {
            // The JPEG JFIF marker stores density and units (0=none/aspect,
            // 1=DPI, 2=dots-per-cm). Parse it directly since `image` doesn't
            // expose this. Scan segments up to the first SOF/EOI.
            let mut i = 0usize;
            if data.len() < 4 || data[0] != 0xFF || data[1] != 0xD8 {
                return None;
            }
            i += 2;
            while i + 4 <= data.len() {
                if data[i] != 0xFF {
                    return None;
                }
                let marker = data[i + 1];
                i += 2;
                // Standalone markers with no length field.
                if marker == 0xD8 || marker == 0xD9 || (0xD0..=0xD7).contains(&marker) {
                    continue;
                }
                if i + 2 > data.len() {
                    return None;
                }
                let seg_len = u16::from_be_bytes([data[i], data[i + 1]]) as usize;
                if seg_len < 2 || i + seg_len > data.len() {
                    return None;
                }
                // APP0 with "JFIF\0" identifier carries the density fields.
                if marker == 0xE0 && seg_len >= 16 && &data[i + 2..i + 7] == b"JFIF\0" {
                    let units = data[i + 9];
                    let x_density = u16::from_be_bytes([data[i + 10], data[i + 11]]) as f32;
                    let y_density = u16::from_be_bytes([data[i + 12], data[i + 13]]) as f32;
                    return match units {
                        1 if x_density > 1.0 && y_density > 1.0 => Some((x_density, y_density)),
                        2 if x_density > 1.0 && y_density > 1.0 => {
                            // dots-per-cm → dots-per-inch
                            Some((x_density * 2.54, y_density * 2.54))
                        }
                        _ => None,
                    };
                }
                i += seg_len;
            }
            None
        }
        _ => None,
    }
}

/// Parse the PNG `pHYs` chunk (pixels-per-unit + unit specifier) to derive DPI.
///
/// Layout: 8-byte signature, then repeating chunks of
/// `[len:u32 be][type:4 bytes][data:len bytes][crc:u32]`. We scan for `pHYs`
/// (which must appear before IDAT per spec) and stop at IDAT/IEND. Its 9-byte
/// payload is `ppu_x:u32, ppu_y:u32, unit:u8` where unit 1 = meter and unit 0
/// = unspecified (aspect ratio only, not convertible to DPI).
fn read_png_dpi(data: &[u8]) -> Option<(f32, f32)> {
    const PNG_SIG: &[u8] = b"\x89PNG\r\n\x1a\n";
    if data.len() < PNG_SIG.len() + 12 || &data[..PNG_SIG.len()] != PNG_SIG {
        return None;
    }
    let mut i = PNG_SIG.len();
    while i + 12 <= data.len() {
        let len = u32::from_be_bytes([data[i], data[i + 1], data[i + 2], data[i + 3]]) as usize;
        let ty = &data[i + 4..i + 8];
        let body = i + 8;
        if body + len + 4 > data.len() {
            return None;
        }
        if ty == b"pHYs" && len == 9 {
            let ppu_x =
                u32::from_be_bytes([data[body], data[body + 1], data[body + 2], data[body + 3]]);
            let ppu_y = u32::from_be_bytes([
                data[body + 4],
                data[body + 5],
                data[body + 6],
                data[body + 7],
            ]);
            let unit = data[body + 8];
            // Unit 1 = meter; unit 0 = aspect-ratio only (no physical scale).
            if unit != 1 {
                return None;
            }
            // pixels-per-meter → pixels-per-inch (1 inch = 0.0254 m)
            let dpi_x = ppu_x as f32 * 0.0254;
            let dpi_y = ppu_y as f32 * 0.0254;
            if dpi_x > 1.0 && dpi_y > 1.0 {
                return Some((dpi_x, dpi_y));
            }
            return None;
        }
        // pHYs must precede IDAT per spec; stop early once we hit image data.
        if ty == b"IDAT" || ty == b"IEND" {
            return None;
        }
        i = body + len + 4; // skip payload + CRC
    }
    None
}

/// Parse the width/height and channel count out of a JPEG's SOF (Start Of
/// Frame) marker without decoding the pixels. Returns `(width, height,
/// components)` where `components` is 1 (grayscale), 3 (YCbCr/RGB), or 4
/// (CMYK/YCCK).
fn read_jpeg_dimensions(data: &[u8]) -> Option<(u32, u32, u8)> {
    if data.len() < 4 || data[0] != 0xFF || data[1] != 0xD8 {
        return None;
    }
    let mut i = 2usize;
    while i + 4 <= data.len() {
        if data[i] != 0xFF {
            return None;
        }
        let marker = data[i + 1];
        i += 2;
        // Standalone markers with no length field.
        if marker == 0xD8 || marker == 0xD9 || (0xD0..=0xD7).contains(&marker) {
            continue;
        }
        if i + 2 > data.len() {
            return None;
        }
        let seg_len = u16::from_be_bytes([data[i], data[i + 1]]) as usize;
        if seg_len < 2 || i + seg_len > data.len() {
            return None;
        }
        // SOF0..SOF15 excluding DHT (0xC4), JPG (0xC8), DAC (0xCC): baseline,
        // progressive, and their variants all share this layout.
        let is_sof =
            (0xC0..=0xCF).contains(&marker) && marker != 0xC4 && marker != 0xC8 && marker != 0xCC;
        if is_sof && seg_len >= 8 {
            let height = u16::from_be_bytes([data[i + 3], data[i + 4]]) as u32;
            let width = u16::from_be_bytes([data[i + 5], data[i + 6]]) as u32;
            let components = data[i + 7];
            return Some((width, height, components));
        }
        i += seg_len;
    }
    None
}

/// Rasterizes an SVG file to RGBA8 bytes + dimensions using resvg.
fn rasterize_svg(data: &[u8]) -> Result<(Vec<u8>, u32, u32), io::Error> {
    let opt = Options::default();
    let tree = Tree::from_data(data, &opt).map_err(|e| {
        io::Error::new(
            io::ErrorKind::InvalidInput,
            format!("Cannot parse SVG: {}", e),
        )
    })?;

    let size = tree.size();
    let width = size.width().ceil() as u32;
    let height = size.height().ceil() as u32;

    let mut pixmap = Pixmap::new(width.max(1), height.max(1))
        .ok_or_else(|| io::Error::new(io::ErrorKind::InvalidData, "could not read pixmap"))?;

    resvg::render(
        &tree,
        resvg::tiny_skia::Transform::identity(),
        &mut pixmap.as_mut(),
    );

    // tiny_skia's Pixmap stores premultiplied RGBA; un-premultiply so the
    // PDF's separate RGB/SMask streams composite correctly.
    let mut rgba = pixmap.data().to_vec();
    for px in rgba.chunks_exact_mut(4) {
        let a = px[3];
        if a != 0 && a != 255 {
            px[0] = ((px[0] as u16 * 255) / a as u16) as u8;
            px[1] = ((px[1] as u16 * 255) / a as u16) as u8;
            px[2] = ((px[2] as u16 * 255) / a as u16) as u8;
        }
    }

    Ok((rgba, width, height))
}

/// Describes an image ready to be written into the PDF, in whatever
/// encoding is cheapest for the caller to produce.
struct EmbeddedImage {
    width: u32,
    height: u32,
    dpi_x: f32,
    dpi_y: f32,
    payload: ImagePayload,
}

enum ImagePayload {
    /// JPEG passthrough: the original compressed bytes are copied verbatim
    /// into a `/DCTDecode` XObject. This is what ImageMagick does for JPEG
    /// input and it avoids a full decode + zlib re-encode round-trip.
    Jpeg { bytes: Vec<u8>, components: u8 },
    /// Decoded raster, to be zlib-compressed and embedded as `/FlateDecode`.
    Flate(PixelData),
}

/// Decode / analyse the input file and produce an `EmbeddedImage`.
fn prepare_image(data: Vec<u8>) -> Result<EmbeddedImage, io::Error> {
    let is_svg = file_format::FileFormat::from_bytes(&data)
        .eq(&file_format::FileFormat::ScalableVectorGraphics);

    if is_svg {
        let (rgba, width, height) = rasterize_svg(&data)?;
        let (rgb, alpha) = separate_rgb_and_alpha_from_rgba(&rgba);
        // SVG has no intrinsic DPI — resvg rasterizes at CSS px which the PDF
        // spec treats as equivalent to points (1/72").
        return Ok(EmbeddedImage {
            width,
            height,
            dpi_x: DEFAULT_IMAGE_DPI,
            dpi_y: DEFAULT_IMAGE_DPI,
            payload: ImagePayload::Flate(PixelData::RgbWithAlpha { rgb, alpha }),
        });
    }

    // JPEG fast path: no decode, no re-encode. Parse just enough of the
    // container to fill in the XObject dictionary and hand the compressed
    // bytes to the PDF viewer via `/DCTDecode`.
    if image::guess_format(&data).ok() == Some(ImageFormat::Jpeg)
        && let Some((width, height, components)) = read_jpeg_dimensions(&data)
    {
        // Only pass through color spaces PDF's DCTDecode understands
        // directly. Anything exotic falls through to the decode path.
        if matches!(components, 1 | 3 | 4) {
            let (dpi_x, dpi_y) =
                read_image_dpi(&data).unwrap_or((DEFAULT_IMAGE_DPI, DEFAULT_IMAGE_DPI));
            return Ok(EmbeddedImage {
                width,
                height,
                dpi_x,
                dpi_y,
                payload: ImagePayload::Jpeg {
                    bytes: data,
                    components,
                },
            });
        }
    }

    // General raster path: decode with `image`, then keep only the channels
    // we actually need. Skipping the alpha split when the source has no
    // alpha halves the pixel data we hand to zlib and drops the `/SMask`
    // XObject entirely.
    let img = image::load_from_memory(&data).map_err(|e| {
        io::Error::new(
            io::ErrorKind::InvalidInput,
            format!("Cannot load image: {}", e),
        )
    })?;
    let (width, height) = img.dimensions();
    let (dpi_x, dpi_y) = read_image_dpi(&data).unwrap_or((DEFAULT_IMAGE_DPI, DEFAULT_IMAGE_DPI));

    let pixels = if img.color().has_alpha() {
        let rgba = img.to_rgba8().into_raw();
        let (rgb, alpha) = separate_rgb_and_alpha_from_rgba(&rgba);
        PixelData::RgbWithAlpha { rgb, alpha }
    } else {
        PixelData::Rgb(img.into_rgb8().into_raw())
    };

    Ok(EmbeddedImage {
        width,
        height,
        dpi_x,
        dpi_y,
        payload: ImagePayload::Flate(pixels),
    })
}

fn convert_image_to_pdf(data: Vec<u8>) -> Result<Vec<u8>, io::Error> {
    let EmbeddedImage {
        width,
        height,
        dpi_x,
        dpi_y,
        payload,
    } = prepare_image(data)?;

    // Size the PDF page in points so the embedded image is displayed at its
    // native physical resolution. A 2400×3000 300-DPI scan becomes an
    // 8"×10" (576×720 pt) page rather than a nonsensical 33"×42" one.
    // The image XObject stays at full pixel resolution; only the CTM shrinks.
    let page_width_pt = width as f32 * 72.0 / dpi_x;
    let page_height_pt = height as f32 * 72.0 / dpi_y;

    // Object layout depends on whether we need a separate soft-mask XObject.
    //   With SMask:    1=Pages, 2=Image, 3=SMask, 4=Page, 5=Contents, 6=Catalog  (7 entries)
    //   Without SMask: 1=Pages, 2=Image, 3=Page, 4=Contents, 5=Catalog          (6 entries)
    let image_object_id: u32 = 2;

    let mut pdf_data: Vec<u8> = Vec::with_capacity(1 << 16);
    writeln!(pdf_data, "%PDF-1.4")?;

    // Emit the image XObject(s) and remember their byte offsets for xref.
    let image_object_pos = pdf_data.len();
    let mask_object_pos: Option<usize> = match &payload {
        ImagePayload::Jpeg { bytes, components } => {
            let color_space = match components {
                1 => "/DeviceGray",
                4 => "/DeviceCMYK",
                _ => "/DeviceRGB",
            };
            writeln!(
                pdf_data,
                "{} 0 obj\n<< /Type /XObject /Subtype /Image /Width {} /Height {} /ColorSpace {} /BitsPerComponent 8 /Filter /DCTDecode /Length {} >>",
                image_object_id,
                width,
                height,
                color_space,
                bytes.len()
            )?;
            writeln!(pdf_data, "stream")?;
            pdf_data.extend(bytes);
            writeln!(pdf_data, "\nendstream\nendobj")?;
            None
        }
        ImagePayload::Flate(PixelData::Rgb(rgb)) => {
            let rgb_data = deflate(rgb)?;
            writeln!(
                pdf_data,
                "{} 0 obj\n<< /Type /XObject /Subtype /Image /Width {} /Height {} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {} >>",
                image_object_id,
                width,
                height,
                rgb_data.len()
            )?;
            writeln!(pdf_data, "stream")?;
            pdf_data.extend(&rgb_data);
            writeln!(pdf_data, "endstream\nendobj")?;
            None
        }
        ImagePayload::Flate(PixelData::RgbWithAlpha { rgb, alpha }) => {
            let rgb_data = deflate(rgb)?;
            let mask_data = deflate(alpha)?;
            let mask_object_id = image_object_id + 1;
            writeln!(
                pdf_data,
                "{} 0 obj\n<< /Type /XObject /Subtype /Image /Width {} /Height {} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {} /SMask {} 0 R >>",
                image_object_id,
                width,
                height,
                rgb_data.len(),
                mask_object_id
            )?;
            writeln!(pdf_data, "stream")?;
            pdf_data.extend(&rgb_data);
            writeln!(pdf_data, "endstream\nendobj")?;

            let pos = pdf_data.len();
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
            Some(pos)
        }
    };

    // Assign the remaining object ids based on whether the SMask was emitted.
    let next_id = if mask_object_pos.is_some() { 4 } else { 3 };
    let page_object_id = next_id;
    let content_stream_object_id = next_id + 1;
    let catalog_object_id = next_id + 2;

    let page_object_pos = pdf_data.len();
    writeln!(
        pdf_data,
        "{} 0 obj\n<< /Type /Page /Parent 1 0 R /MediaBox [0 0 {:.4} {:.4}] /Contents {} 0 R /Resources << /XObject << /Im{} {} 0 R >> >> >>",
        page_object_id,
        page_width_pt,
        page_height_pt,
        content_stream_object_id,
        image_object_id,
        image_object_id
    )?;
    writeln!(pdf_data, "endobj")?;

    let content_stream_pos = pdf_data.len();
    // The CTM scales the 1×1 unit-square image XObject to fill the page in
    // point-space; MediaBox uses the same values, so together they preserve
    // the source image's physical (DPI-aware) size.
    let content = format!(
        "q\n{:.4} 0 0 {:.4} 0 0 cm\n/Im{} Do\nQ",
        page_width_pt, page_height_pt, image_object_id
    );
    writeln!(
        pdf_data,
        "{} 0 obj\n<< /Length {} >>",
        content_stream_object_id,
        content.len()
    )?;
    writeln!(pdf_data, "stream\n{}\nendstream\nendobj", content)?;

    let pages_object_pos = pdf_data.len();
    writeln!(
        pdf_data,
        "1 0 obj\n<< /Type /Pages /Kids [ {} 0 R ] /Count 1 >>",
        page_object_id
    )?;
    writeln!(pdf_data, "endobj")?;

    let catalog_object_pos = pdf_data.len();
    writeln!(
        pdf_data,
        "{} 0 obj\n<< /Type /Catalog /Pages 1 0 R >>",
        catalog_object_id
    )?;
    writeln!(pdf_data, "endobj")?;

    let xref_start = pdf_data.len();
    let total_objects = catalog_object_id + 1; // ids are 1..=catalog_object_id
    writeln!(pdf_data, "xref")?;
    writeln!(pdf_data, "0 {}", total_objects)?;
    writeln!(pdf_data, "0000000000 65535 f ")?;
    writeln!(pdf_data, "{:010} 00000 n ", pages_object_pos)?;
    writeln!(pdf_data, "{:010} 00000 n ", image_object_pos)?;
    if let Some(pos) = mask_object_pos {
        writeln!(pdf_data, "{:010} 00000 n ", pos)?;
    }
    writeln!(pdf_data, "{:010} 00000 n ", page_object_pos)?;
    writeln!(pdf_data, "{:010} 00000 n ", content_stream_pos)?;
    writeln!(pdf_data, "{:010} 00000 n ", catalog_object_pos)?;

    writeln!(
        pdf_data,
        "trailer\n<< /Size {} /Root {} 0 R >>",
        total_objects, catalog_object_id
    )?;
    writeln!(pdf_data, "startxref\n{}", xref_start)?;
    writeln!(pdf_data, "%%EOF")?;

    Ok(pdf_data)
}

impl Converter for ImageConverter {
    fn supported_formats(&self) -> &'static [&'static str] {
        &[
            "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "svg",
        ]
    }
    /// Convert an image to PDF bytes
    fn convert(&self, input: impl Into<ConversionInput> + Clone) -> io::Result<Vec<u8>> {
        let data;
        match input.into() {
            ConversionInput::Binary(b) => {
                let kind = file_format::FileFormat::from_bytes(&b);
                if self.supported_formats().contains(&kind.extension()) {
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

        convert_image_to_pdf(data)
    }
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
            &[
                "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "svg",
            ]
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
