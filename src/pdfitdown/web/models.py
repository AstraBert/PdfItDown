from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
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


class FeatureType(str, Enum):
    CONVERT = "convert"
    MERGE = "merge"
    SPLIT = "split"
    COMPRESS = "compress"


class CompressionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SplitMode(str, Enum):
    RANGE = "range"
    PAGES = "pages"
    EVERY_N = "every_n"


class UploadedFile(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    original_name: str
    file_size: int
    status: FileStatus = FileStatus.PENDING
    upload_progress: float = 0.0
    conversion_progress: float = 0.0
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.now)


class ConversionTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    files: List[UploadedFile] = Field(default_factory=list)
    pdf_title: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
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


class MergeFileItem(BaseModel):
    file_id: str
    original_name: str
    order: int


class SplitRange(BaseModel):
    start: int
    end: int
    name: Optional[str] = None

    @field_validator('start', 'end')
    @classmethod
    def check_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Page number must be at least 1')
        return v


class SplitRequest(BaseModel):
    mode: SplitMode = SplitMode.RANGE
    ranges: Optional[List[SplitRange]] = None
    pages: Optional[List[int]] = None
    every_n: Optional[int] = None
    output_prefix: Optional[str] = None


class CompressRequest(BaseModel):
    level: CompressionLevel = CompressionLevel.MEDIUM


class OutputFile(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    filename: str
    file_size: int
    output_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def size(self) -> int:
        return self.file_size

    class Config:
        @staticmethod
        def json_schema_extra(schema, model):
            schema['properties']['size'] = {'type': 'integer'}

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data['size'] = self.size
        return data

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data['size'] = self.size
        return data


class FeatureTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    feature_type: FeatureType
    status: TaskStatus = TaskStatus.PENDING
    files: List[UploadedFile] = Field(default_factory=list)
    output_files: List[OutputFile] = Field(default_factory=list)
    options: Dict[str, Any] = Field(default_factory=dict)
    progress: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    zip_path: Optional[str] = None

    @property
    def completed_count(self) -> int:
        return sum(1 for f in self.files if f.status == FileStatus.COMPLETED)

    @property
    def failed_count(self) -> int:
        return sum(1 for f in self.files if f.status == FileStatus.FAILED)


class FeatureTaskResponse(BaseModel):
    task_id: str
    feature_type: FeatureType
    status: TaskStatus
    total_files: int
    completed_count: int
    failed_count: int
    progress: float
    total_progress: float
    files: List[UploadedFile]
    output_files: List[OutputFile]
    outputs: List[OutputFile]
    error_message: Optional[str] = None


class PageInfo(BaseModel):
    page_number: int
    width: float
    height: float


class PageSize(BaseModel):
    width: float
    height: float


class PdfInfoResponse(BaseModel):
    page_count: int
    page_size: Optional[PageSize] = None
    file_size: int
    pages: List[PageInfo] = Field(default_factory=list)
    filename: Optional[str] = None
