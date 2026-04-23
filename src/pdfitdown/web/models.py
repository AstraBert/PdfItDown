from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid


class FileStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    CONVERTING = "converting"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL_FAILED = "partial_failed"
    FAILED = "failed"


class UploadedFile(BaseModel):
    id: str = uuid.uuid4().hex
    original_name: str
    file_size: int
    status: FileStatus = FileStatus.PENDING
    upload_progress: float = 0.0
    conversion_progress: float = 0.0
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    uploaded_at: datetime = datetime.now()


class ConversionTask(BaseModel):
    id: str = uuid.uuid4().hex
    files: List[UploadedFile] = []
    pdf_title: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    zip_path: Optional[str] = None

    @property
    def completed_count(self) -> int:
        return sum(1 for f in self.files if f.status == FileStatus.COMPLETED)

    @property
    def failed_count(self) -> int:
        return sum(1 for f in self.files if f.status == FileStatus.FAILED)

    @property
    def total_progress(self) -> float:
        if not self.files:
            return 0.0
        upload_progress = sum(f.upload_progress for f in self.files) / len(self.files)
        conversion_progress = sum(f.conversion_progress for f in self.files) / len(self.files)
        return (upload_progress + conversion_progress) / 2


class UploadResponse(BaseModel):
    task_id: str
    file_id: str
    filename: str
    status: FileStatus


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    total_files: int
    completed_count: int
    failed_count: int
    total_progress: float
    files: List[UploadedFile]


class StartConversionRequest(BaseModel):
    task_id: str
    pdf_title: Optional[str] = None


class DownloadInfo(BaseModel):
    task_id: str
    filename: str
    download_url: str
    file_size: Optional[int] = None
