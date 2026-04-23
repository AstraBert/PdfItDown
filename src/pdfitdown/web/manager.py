import asyncio
import os
import shutil
import struct
import tempfile
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor
import logging

from ..pdfconversion import Converter
from .models import (
    UploadedFile, ConversionTask, FileStatus, TaskStatus
)

logger = logging.getLogger(__name__)


ZIP_SIGNATURE = b'PK\x03\x04'


def is_zip_format(file_path: str) -> bool:
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == ZIP_SIGNATURE
    except Exception:
        return False


def validate_file(file_path: str, original_name: str) -> tuple[bool, str]:
    suffix = Path(original_name).suffix.lower()
    
    zip_based_extensions = ['.docx', '.xlsx', '.xls', '.pptx', '.zip']
    
    if suffix in zip_based_extensions:
        if not is_zip_format(file_path):
            return False, f"File {original_name} is not a valid ZIP-based format. Please ensure the file is not corrupted."
    
    return True, "OK"


def get_default_work_dir() -> str:
    env_dir = os.environ.get("PDFITDOWN_WORK_DIR")
    if env_dir:
        return env_dir
    
    try:
        project_dir = Path(__file__).parent.parent.parent.parent.parent
        work_dir = project_dir / ".pdfitdown_web"
        work_dir.mkdir(parents=True, exist_ok=True)
        return str(work_dir)
    except Exception:
        return os.path.join(tempfile.gettempdir(), "pdfitdown_web")


class ConversionManager:
    def __init__(self, work_dir: Optional[str] = None):
        self.tasks: Dict[str, ConversionTask] = {}
        self.converter = Converter()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        if work_dir is None:
            work_dir = get_default_work_dir()
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self._upload_dir = self.work_dir / "uploads"
        self._output_dir = self.work_dir / "outputs"
        self._zip_dir = self.work_dir / "zips"
        
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._zip_dir.mkdir(parents=True, exist_ok=True)

    def create_task(self) -> ConversionTask:
        task = ConversionTask()
        self.tasks[task.id] = task
        logger.info(f"Created new task: {task.id}")
        return task

    def get_task(self, task_id: str) -> Optional[ConversionTask]:
        return self.tasks.get(task_id)

    def add_file_to_task(
        self, 
        task_id: str, 
        original_name: str, 
        file_content: bytes,
        file_size: int
    ) -> Optional[UploadedFile]:
        task = self.get_task(task_id)
        if not task:
            return None
        
        if not file_content or len(file_content) == 0:
            logger.error(f"Empty file content received: {original_name}")
            return None
        
        if len(file_content) != file_size:
            logger.warning(f"File size mismatch: expected {file_size}, got {len(file_content)}")
        
        uploaded_file = UploadedFile(
            original_name=original_name,
            file_size=len(file_content),
            status=FileStatus.UPLOADED,
            upload_progress=100.0
        )
        
        task_upload_dir = self._upload_dir / task_id
        task_upload_dir.mkdir(parents=True, exist_ok=True)
        
        suffix = Path(original_name).suffix
        safe_base = self._safe_filename(Path(original_name).stem)
        safe_filename = f"{safe_base}{suffix}" if suffix else safe_base
        
        upload_path = task_upload_dir / f"{uploaded_file.id}_{safe_filename}"
        uploaded_file._upload_path = str(upload_path)
        
        with open(upload_path, "wb") as f:
            f.write(file_content)
        
        actual_size = os.path.getsize(upload_path)
        if actual_size != len(file_content):
            logger.error(f"File write failed: expected {len(file_content)} bytes, wrote {actual_size} bytes")
            return None
        
        task.files.append(uploaded_file)
        logger.info(f"Added file {uploaded_file.id} ({original_name}) to task {task_id}, saved to {upload_path}, size: {actual_size} bytes")
        return uploaded_file

    def _safe_filename(self, filename: str) -> str:
        safe_chars = []
        for c in filename:
            if c.isalnum() or c in "._- ":
                safe_chars.append(c)
            elif ord(c) > 127:
                safe_chars.append(c)
            else:
                safe_chars.append("_")
        result = "".join(safe_chars).strip()
        if not result or result.startswith("."):
            result = "file_" + result.lstrip(".")
        return result if result else "unnamed_file"

    async def convert_task(
        self, 
        task_id: str, 
        pdf_title: Optional[str] = None
    ) -> ConversionTask:
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.status = TaskStatus.PROCESSING
        if pdf_title:
            task.pdf_title = pdf_title
        
        task_output_dir = self._output_dir / task_id
        task_output_dir.mkdir(parents=True, exist_ok=True)
        
        loop = asyncio.get_event_loop()
        
        async def convert_file(file: UploadedFile) -> UploadedFile:
            file.status = FileStatus.CONVERTING
            file.conversion_progress = 0.0
            
            try:
                upload_path = getattr(file, '_upload_path', None)
                if not upload_path or not os.path.exists(upload_path):
                    raise FileNotFoundError(f"Uploaded file not found: {file.id}")
                
                file_size = os.path.getsize(upload_path)
                logger.info(f"Converting file {file.id} ({file.original_name}), path: {upload_path}, size: {file_size} bytes")
                
                is_valid, validation_msg = validate_file(upload_path, file.original_name)
                if not is_valid:
                    raise ValueError(validation_msg)
                
                suffix = Path(file.original_name).suffix.lower()
                logger.info(f"File {file.id} has suffix: {suffix}")
                
                safe_original = self._safe_filename(file.original_name)
                output_filename = Path(safe_original).stem + ".pdf"
                output_path = task_output_dir / f"{file.id}_{output_filename}"
                
                file.conversion_progress = 30.0
                
                result = await loop.run_in_executor(
                    self.executor,
                    lambda: self.converter.convert(
                        file_path=str(upload_path),
                        output_path=str(output_path),
                        title=pdf_title or file.original_name,
                        overwrite=True
                    )
                )
                
                if result is None:
                    raise Exception("Conversion returned None")
                
                if not os.path.exists(output_path):
                    raise Exception(f"Output file not created: {output_path}")
                
                output_size = os.path.getsize(output_path)
                logger.info(f"Conversion successful for {file.id}, output size: {output_size} bytes")
                
                file.conversion_progress = 100.0
                file.status = FileStatus.COMPLETED
                file.output_path = str(output_path)
                logger.info(f"Successfully converted file {file.id}")
                
            except Exception as e:
                file.status = FileStatus.FAILED
                file.error_message = str(e)
                logger.error(f"Failed to convert file {file.id} ({file.original_name}): {e}")
            
            return file
        
        tasks = [convert_file(file) for file in task.files]
        await asyncio.gather(*tasks)
        
        completed = task.completed_count
        failed = task.failed_count
        total = len(task.files)
        
        if completed == total:
            task.status = TaskStatus.COMPLETED
        elif completed > 0:
            task.status = TaskStatus.PARTIAL_FAILED
        else:
            task.status = TaskStatus.FAILED
        
        task.completed_at = datetime.now()
        logger.info(f"Task {task_id} completed: {completed}/{total} succeeded, {failed} failed")
        
        return task

    def create_zip(self, task_id: str) -> Optional[str]:
        task = self.get_task(task_id)
        if not task:
            return None
        
        completed_files = [
            f for f in task.files 
            if f.status == FileStatus.COMPLETED and f.output_path
        ]
        
        if not completed_files:
            return None
        
        zip_path = self._zip_dir / f"{task_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in completed_files:
                if file.output_path and os.path.exists(file.output_path):
                    base_name = Path(file.original_name).stem
                    if not base_name or base_name.isspace():
                        base_name = f"file_{file.id[:8]}"
                    arcname = f"{base_name}.pdf"
                    
                    zip_info = zipfile.ZipInfo(arcname)
                    zip_info.compress_type = zipfile.ZIP_DEFLATED
                    zip_info.create_system = 3
                    
                    with open(file.output_path, 'rb') as f:
                        zf.writestr(zip_info, f.read())
                    
                    logger.info(f"Added to ZIP: {arcname}")
        
        task.zip_path = str(zip_path)
        logger.info(f"Created ZIP for task {task_id}: {zip_path}")
        return str(zip_path)

    def cleanup_task(self, task_id: str) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        
        try:
            task_upload_dir = self._upload_dir / task_id
            if task_upload_dir.exists():
                shutil.rmtree(task_upload_dir)
            
            task_output_dir = self._output_dir / task_id
            if task_output_dir.exists():
                shutil.rmtree(task_output_dir)
            
            if task.zip_path and os.path.exists(task.zip_path):
                os.remove(task.zip_path)
            
            del self.tasks[task_id]
            logger.info(f"Cleaned up task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup task {task_id}: {e}")
            return False

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        now = datetime.now()
        task_ids_to_clean = []
        
        for task_id, task in self.tasks.items():
            if task.completed_at:
                age_hours = (now - task.completed_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    task_ids_to_clean.append(task_id)
        
        for task_id in task_ids_to_clean:
            self.cleanup_task(task_id)


conversion_manager = ConversionManager()
