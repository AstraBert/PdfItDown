import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging

from .models import CompressionLevel, SplitRange, SplitMode

logger = logging.getLogger(__name__)

try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF (fitz) not available, some PDF features may be limited")

try:
    import pikepdf
    PIKEPDF_AVAILABLE = True
except ImportError:
    PIKEPDF_AVAILABLE = False
    logger.warning("pikepdf not available, compression features may be limited")


class PdfProcessor:
    def __init__(self):
        if not PYMUPDF_AVAILABLE and not PIKEPDF_AVAILABLE:
            raise RuntimeError(
                "Neither PyMuPDF nor pikepdf is available. "
                "Please install at least one: pip install pymupdf or pip install pikepdf"
            )

    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        if not PYMUPDF_AVAILABLE:
            return self._get_pdf_info_pikepdf(pdf_path)
        return self._get_pdf_info_fitz(pdf_path)

    def _get_pdf_info_fitz(self, pdf_path: str) -> Dict[str, Any]:
        doc = fitz.open(pdf_path)
        try:
            page_count = len(doc)
            file_size = os.path.getsize(pdf_path)
            filename = Path(pdf_path).name
            
            page_size_obj = None
            if page_count > 0:
                first_page = doc[0]
                rect = first_page.rect
                width = round(rect.width, 2)
                height = round(rect.height, 2)
                page_size_obj = {"width": width, "height": height}
            
            pages = []
            for i, page in enumerate(doc):
                rect = page.rect
                pages.append({
                    "page_number": i + 1,
                    "width": round(rect.width, 2),
                    "height": round(rect.height, 2)
                })
            
            return {
                "page_count": page_count,
                "page_size": page_size_obj,
                "file_size": file_size,
                "pages": pages,
                "filename": filename
            }
        finally:
            doc.close()

    def _get_pdf_info_pikepdf(self, pdf_path: str) -> Dict[str, Any]:
        with pikepdf.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            file_size = os.path.getsize(pdf_path)
            filename = Path(pdf_path).name
            
            page_size_obj = {"width": 595.0, "height": 842.0}
            
            pages = []
            for i in range(page_count):
                pages.append({
                    "page_number": i + 1,
                    "width": 595.0,
                    "height": 842.0
                })
            
            return {
                "page_count": page_count,
                "page_size": page_size_obj,
                "file_size": file_size,
                "pages": pages,
                "filename": filename
            }

    def merge_pdfs(
        self,
        input_paths: List[str],
        output_path: str,
        order: Optional[List[int]] = None
    ) -> str:
        if order is None:
            order = list(range(len(input_paths)))
        
        if len(order) != len(input_paths):
            raise ValueError("Order list length must match input paths length")
        
        if PYMUPDF_AVAILABLE:
            return self._merge_pdfs_fitz(input_paths, output_path, order)
        elif PIKEPDF_AVAILABLE:
            return self._merge_pdfs_pikepdf(input_paths, output_path, order)
        else:
            raise RuntimeError("No PDF library available for merging")

    def _merge_pdfs_fitz(
        self,
        input_paths: List[str],
        output_path: str,
        order: List[int]
    ) -> str:
        merged_doc = fitz.open()
        
        try:
            for idx in order:
                if idx < 0 or idx >= len(input_paths):
                    raise ValueError(f"Invalid order index: {idx}")
                
                input_path = input_paths[idx]
                if not os.path.exists(input_path):
                    raise FileNotFoundError(f"Input file not found: {input_path}")
                
                with fitz.open(input_path) as doc:
                    merged_doc.insert_pdf(doc)
                    logger.info(f"Merged: {input_path} ({len(doc)} pages)")
            
            merged_doc.save(output_path)
            logger.info(f"Merge complete: {output_path} ({len(merged_doc)} pages)")
            return output_path
        finally:
            merged_doc.close()

    def _merge_pdfs_pikepdf(
        self,
        input_paths: List[str],
        output_path: str,
        order: List[int]
    ) -> str:
        from pikepdf import Pdf
        
        merged = Pdf.new()
        
        for idx in order:
            if idx < 0 or idx >= len(input_paths):
                raise ValueError(f"Invalid order index: {idx}")
            
            input_path = input_paths[idx]
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            with Pdf.open(input_path) as src:
                for page in src.pages:
                    merged.pages.append(page)
                logger.info(f"Merged: {input_path} ({len(src.pages)} pages)")
        
        merged.save(output_path)
        logger.info(f"Merge complete: {output_path} ({len(merged.pages)} pages)")
        return output_path

    def split_pdf(
        self,
        input_path: str,
        output_dir: str,
        mode: SplitMode = SplitMode.RANGE,
        ranges: Optional[List[SplitRange]] = None,
        pages: Optional[List[int]] = None,
        every_n: Optional[int] = None,
        output_prefix: Optional[str] = None
    ) -> List[str]:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = output_prefix or Path(input_path).stem
        
        if PYMUPDF_AVAILABLE:
            return self._split_pdf_fitz(
                input_path, output_dir, mode, ranges, pages, every_n, base_name
            )
        elif PIKEPDF_AVAILABLE:
            return self._split_pdf_pikepdf(
                input_path, output_dir, mode, ranges, pages, every_n, base_name
            )
        else:
            raise RuntimeError("No PDF library available for splitting")

    def _split_pdf_fitz(
        self,
        input_path: str,
        output_dir: str,
        mode: SplitMode,
        ranges: Optional[List[SplitRange]],
        pages: Optional[List[int]],
        every_n: Optional[int],
        base_name: str
    ) -> List[str]:
        output_files = []
        
        with fitz.open(input_path) as doc:
            total_pages = len(doc)
            logger.info(f"Splitting PDF: {input_path} ({total_pages} pages)")
            
            if mode == SplitMode.RANGE and ranges:
                for i, rng in enumerate(ranges):
                    start = rng.start - 1
                    end = rng.end
                    
                    if start < 0:
                        start = 0
                    if end > total_pages:
                        end = total_pages
                    
                    if start >= end:
                        logger.warning(f"Invalid range: {rng.start}-{rng.end}, skipping")
                        continue
                    
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
                    
                    range_name = rng.name or f"part_{i + 1}"
                    output_path = os.path.join(output_dir, f"{base_name}_{range_name}.pdf")
                    new_doc.save(output_path)
                    new_doc.close()
                    
                    output_files.append(output_path)
                    logger.info(f"Created: {output_path} (pages {rng.start}-{rng.end})")
            
            elif mode == SplitMode.PAGES and pages:
                for page_num in pages:
                    idx = page_num - 1
                    if idx < 0 or idx >= total_pages:
                        logger.warning(f"Invalid page number: {page_num}, skipping")
                        continue
                    
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=idx, to_page=idx)
                    
                    output_path = os.path.join(output_dir, f"{base_name}_page_{page_num}.pdf")
                    new_doc.save(output_path)
                    new_doc.close()
                    
                    output_files.append(output_path)
                    logger.info(f"Created: {output_path} (page {page_num})")
            
            elif mode == SplitMode.EVERY_N and every_n:
                if every_n <= 0:
                    raise ValueError("every_n must be greater than 0")
                
                part_num = 1
                for start in range(0, total_pages, every_n):
                    end = min(start + every_n, total_pages)
                    
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
                    
                    output_path = os.path.join(
                        output_dir, 
                        f"{base_name}_part_{part_num}.pdf"
                    )
                    new_doc.save(output_path)
                    new_doc.close()
                    
                    output_files.append(output_path)
                    logger.info(f"Created: {output_path} (pages {start + 1}-{end})")
                    part_num += 1
            
            else:
                for i in range(total_pages):
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=i, to_page=i)
                    
                    output_path = os.path.join(output_dir, f"{base_name}_page_{i + 1}.pdf")
                    new_doc.save(output_path)
                    new_doc.close()
                    
                    output_files.append(output_path)
                    logger.info(f"Created: {output_path} (page {i + 1})")
        
        return output_files

    def _split_pdf_pikepdf(
        self,
        input_path: str,
        output_dir: str,
        mode: SplitMode,
        ranges: Optional[List[SplitRange]],
        pages: Optional[List[int]],
        every_n: Optional[int],
        base_name: str
    ) -> List[str]:
        from pikepdf import Pdf
        
        output_files = []
        
        with Pdf.open(input_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"Splitting PDF: {input_path} ({total_pages} pages)")
            
            if mode == SplitMode.RANGE and ranges:
                for i, rng in enumerate(ranges):
                    start = rng.start - 1
                    end = rng.end
                    
                    if start < 0:
                        start = 0
                    if end > total_pages:
                        end = total_pages
                    
                    if start >= end:
                        logger.warning(f"Invalid range: {rng.start}-{rng.end}, skipping")
                        continue
                    
                    new_pdf = Pdf.new()
                    for page_idx in range(start, end):
                        new_pdf.pages.append(pdf.pages[page_idx])
                    
                    range_name = rng.name or f"part_{i + 1}"
                    output_path = os.path.join(output_dir, f"{base_name}_{range_name}.pdf")
                    new_pdf.save(output_path)
                    
                    output_files.append(output_path)
                    logger.info(f"Created: {output_path} (pages {rng.start}-{rng.end})")
            
            elif mode == SplitMode.PAGES and pages:
                for page_num in pages:
                    idx = page_num - 1
                    if idx < 0 or idx >= total_pages:
                        logger.warning(f"Invalid page number: {page_num}, skipping")
                        continue
                    
                    new_pdf = Pdf.new()
                    new_pdf.pages.append(pdf.pages[idx])
                    
                    output_path = os.path.join(output_dir, f"{base_name}_page_{page_num}.pdf")
                    new_pdf.save(output_path)
                    
                    output_files.append(output_path)
                    logger.info(f"Created: {output_path} (page {page_num})")
            
            elif mode == SplitMode.EVERY_N and every_n:
                if every_n <= 0:
                    raise ValueError("every_n must be greater than 0")
                
                part_num = 1
                for start in range(0, total_pages, every_n):
                    end = min(start + every_n, total_pages)
                    
                    new_pdf = Pdf.new()
                    for page_idx in range(start, end):
                        new_pdf.pages.append(pdf.pages[page_idx])
                    
                    output_path = os.path.join(
                        output_dir, 
                        f"{base_name}_part_{part_num}.pdf"
                    )
                    new_pdf.save(output_path)
                    
                    output_files.append(output_path)
                    logger.info(f"Created: {output_path} (pages {start + 1}-{end})")
                    part_num += 1
            
            else:
                for i in range(total_pages):
                    new_pdf = Pdf.new()
                    new_pdf.pages.append(pdf.pages[i])
                    
                    output_path = os.path.join(output_dir, f"{base_name}_page_{i + 1}.pdf")
                    new_pdf.save(output_path)
                    
                    output_files.append(output_path)
                    logger.info(f"Created: {output_path} (page {i + 1})")
        
        return output_files

    def compress_pdf(
        self,
        input_path: str,
        output_path: str,
        level: CompressionLevel = CompressionLevel.MEDIUM
    ) -> str:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        original_size = os.path.getsize(input_path)
        logger.info(f"Compressing PDF: {input_path} ({original_size} bytes), level: {level}")
        
        if PIKEPDF_AVAILABLE:
            result = self._compress_pdf_pikepdf(input_path, output_path, level)
        elif PYMUPDF_AVAILABLE:
            result = self._compress_pdf_fitz(input_path, output_path, level)
        else:
            raise RuntimeError("No PDF library available for compression")
        
        compressed_size = os.path.getsize(result)
        ratio = (1 - compressed_size / original_size) * 100
        logger.info(f"Compression complete: {result}")
        logger.info(f"Original: {original_size} bytes, Compressed: {compressed_size} bytes, Reduction: {ratio:.1f}%")
        
        return result

    def _compress_pdf_pikepdf(
        self,
        input_path: str,
        output_path: str,
        level: CompressionLevel
    ) -> str:
        from pikepdf import Pdf, PdfImage
        
        with Pdf.open(input_path) as pdf:
            for page in pdf.pages:
                self._process_page_images_pikepdf(page, level)
            
            compression_settings = {}
            
            if level == CompressionLevel.HIGH:
                compression_settings = {
                    "compress_streams": True,
                    "object_stream_mode": pikepdf.ObjectStreamMode.generate,
                    "stream_decode_level": 1,
                }
            elif level == CompressionLevel.MEDIUM:
                compression_settings = {
                    "compress_streams": True,
                    "object_stream_mode": pikepdf.ObjectStreamMode.generate,
                }
            else:
                compression_settings = {
                    "compress_streams": True,
                }
            
            pdf.save(output_path, **compression_settings)
        
        return output_path

    def _process_page_images_pikepdf(self, page, level: CompressionLevel):
        from pikepdf import PdfImage
        
        if '/Resources' not in page:
            return
        
        resources = page['/Resources']
        
        if '/XObject' not in resources:
            return
        
        xobjects = resources['/XObject']
        
        for key in list(xobjects.keys()):
            xobj = xobjects[key]
            
            if '/Subtype' in xobj and xobj['/Subtype'] == '/Image':
                try:
                    pdf_image = PdfImage(xobj)
                    
                    if level == CompressionLevel.HIGH:
                        raw_image = pdf_image.as_pil_image()
                        
                        if raw_image.mode in ['RGBA', 'RGBa', 'LA', 'La']:
                            raw_image = raw_image.convert('RGB')
                        
                        max_dimension = 1920
                        if raw_image.width > max_dimension or raw_image.height > max_dimension:
                            ratio = min(max_dimension / raw_image.width, max_dimension / raw_image.height)
                            new_size = (int(raw_image.width * ratio), int(raw_image.height * ratio))
                            raw_image = raw_image.resize(new_size, resample=3)
                        
                        pdf_image = PdfImage.from_pil_image(raw_image)
                        xobj.write(pdf_image.read(), filter=pikepdf.Name('/DCTDecode'))
                    
                    elif level == CompressionLevel.MEDIUM:
                        raw_image = pdf_image.as_pil_image()
                        
                        if raw_image.mode in ['RGBA', 'RGBa', 'LA', 'La']:
                            raw_image = raw_image.convert('RGB')
                        
                        max_dimension = 2560
                        if raw_image.width > max_dimension or raw_image.height > max_dimension:
                            ratio = min(max_dimension / raw_image.width, max_dimension / raw_image.height)
                            new_size = (int(raw_image.width * ratio), int(raw_image.height * ratio))
                            raw_image = raw_image.resize(new_size, resample=3)
                        
                        pdf_image = PdfImage.from_pil_image(raw_image)
                        xobj.write(pdf_image.read(), filter=pikepdf.Name('/DCTDecode'))
                
                except Exception as e:
                    logger.warning(f"Failed to process image {key}: {e}")

    def _compress_pdf_fitz(
        self,
        input_path: str,
        output_path: str,
        level: CompressionLevel
    ) -> str:
        doc = fitz.open(input_path)
        
        try:
            if level in [CompressionLevel.MEDIUM, CompressionLevel.HIGH]:
                for i in range(len(doc)):
                    page = doc[i]
                    
                    images = page.get_images()
                    for img in images:
                        xref = img[0]
                        smask = img[1]
                        
                        try:
                            pix = fitz.Pixmap(doc, xref)
                            
                            if level == CompressionLevel.HIGH:
                                if pix.n >= 4:
                                    pix = fitz.Pixmap(fitz.csRGB, pix)
                                
                                max_dimension = 1920
                                if pix.width > max_dimension or pix.height > max_dimension:
                                    ratio = min(max_dimension / pix.width, max_dimension / pix.height)
                                    new_width = int(pix.width * ratio)
                                    new_height = int(pix.height * ratio)
                                    pix = fitz.Pixmap(pix, new_width, new_height)
                                
                                new_data = pix.tobytes("jpeg", quality=60)
                                doc.update_stream(xref, new_data)
                                
                                if smask > 0:
                                    try:
                                        smask_pix = fitz.Pixmap(doc, smask)
                                        if smask_pix.width > max_dimension or smask_pix.height > max_dimension:
                                            smask_pix = fitz.Pixmap(smask_pix, new_width, new_height)
                                        smask_data = smask_pix.tobytes("jpeg", quality=60)
                                        doc.update_stream(smask, smask_data)
                                    except:
                                        pass
                            
                            elif level == CompressionLevel.MEDIUM:
                                if pix.n >= 4:
                                    pix = fitz.Pixmap(fitz.csRGB, pix)
                                
                                max_dimension = 2560
                                if pix.width > max_dimension or pix.height > max_dimension:
                                    ratio = min(max_dimension / pix.width, max_dimension / pix.height)
                                    new_width = int(pix.width * ratio)
                                    new_height = int(pix.height * ratio)
                                    pix = fitz.Pixmap(pix, new_width, new_height)
                                
                                new_data = pix.tobytes("jpeg", quality=80)
                                doc.update_stream(xref, new_data)
                                
                                if smask > 0:
                                    try:
                                        smask_pix = fitz.Pixmap(doc, smask)
                                        if smask_pix.width > max_dimension or smask_pix.height > max_dimension:
                                            smask_pix = fitz.Pixmap(smask_pix, new_width, new_height)
                                        smask_data = smask_pix.tobytes("jpeg", quality=80)
                                        doc.update_stream(smask, smask_data)
                                    except:
                                        pass
                        
                        except Exception as e:
                            logger.warning(f"Failed to process image xref={xref}: {e}")
            
            doc.save(
                output_path,
                garbage=4,
                deflate=True,
                clean=True,
                linear=True
            )
            
            return output_path
        finally:
            doc.close()


pdf_processor = PdfProcessor()
