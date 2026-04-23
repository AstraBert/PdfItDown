import os
import json
from pathlib import Path
from typing import Optional, List
import logging

from fastapi import (
    FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Body
)
from fastapi.responses import (
    HTMLResponse, Response
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .models import (
    UploadResponse, TaskStatusResponse, FileStatus, TaskStatus,
    FeatureType, CompressionLevel, SplitMode, SplitRange,
    FeatureTaskResponse, PdfInfoResponse, CompressRequest, SplitRequest
)
from .manager import conversion_manager, feature_manager

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


def sanitize_filename(filename: str) -> str:
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


def create_app() -> FastAPI:
    app = FastAPI(
        title="PdfItDown Web",
        description="Web interface for PdfItDown - Convert Everything to PDF",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def index():
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(
            content="<html><body><h1>PdfItDown Web Service</h1></body></html>"
        )
    
    @app.post("/api/tasks/create", response_model=dict)
    async def create_task():
        task = conversion_manager.create_task()
        return {"task_id": task.id}
    
    @app.post("/api/tasks/{task_id}/upload", response_model=UploadResponse)
    async def upload_file(
        task_id: str,
        file: UploadFile = File(...)
    ):
        task = conversion_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        file_content = await file.read()
        file_size = len(file_content)
        
        uploaded_file = conversion_manager.add_file_to_task(
            task_id=task_id,
            original_name=file.filename or "unnamed_file",
            file_content=file_content,
            file_size=file_size
        )
        
        if not uploaded_file:
            raise HTTPException(status_code=500, detail="Failed to upload file")
        
        return UploadResponse(
            task_id=task_id,
            file_id=uploaded_file.id,
            filename=uploaded_file.original_name,
            status=uploaded_file.status
        )
    
    @app.get("/api/tasks/{task_id}/status", response_model=TaskStatusResponse)
    async def get_task_status(task_id: str):
        task = conversion_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskStatusResponse(
            task_id=task.id,
            status=task.status,
            total_files=len(task.files),
            completed_count=task.completed_count,
            failed_count=task.failed_count,
            total_progress=task.total_progress,
            files=task.files
        )
    
    @app.post("/api/tasks/{task_id}/convert")
    async def start_conversion(
        task_id: str,
        background_tasks: BackgroundTasks,
        pdf_title: Optional[str] = Form(None)
    ):
        task = conversion_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if not task.files:
            raise HTTPException(status_code=400, detail="No files in task")
        
        async def run_conversion():
            await conversion_manager.convert_task(task_id, pdf_title)
        
        background_tasks.add_task(run_conversion)
        
        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Conversion started"
        }
    
    @app.get("/api/tasks/{task_id}/download/zip")
    async def download_zip(task_id: str):
        task = conversion_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.status not in [TaskStatus.COMPLETED, TaskStatus.PARTIAL_FAILED]:
            raise HTTPException(status_code=400, detail="Task not completed")
        
        if not task.zip_path:
            zip_path = conversion_manager.create_zip(task_id)
            if not zip_path:
                raise HTTPException(
                    status_code=400, 
                    detail="No completed files to zip"
                )
        else:
            zip_path = task.zip_path
        
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="Zip file not found")
        
        zip_filename = f"converted_{task_id[:8]}.zip"
        
        with open(zip_path, "rb") as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=\"{zip_filename}\"",
                "Content-Length": str(len(content)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    
    @app.get("/api/tasks/{task_id}/download/{file_id}")
    async def download_file(task_id: str, file_id: str):
        task = conversion_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        file = next((f for f in task.files if f.id == file_id), None)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file.status != FileStatus.COMPLETED or not file.output_path:
            raise HTTPException(status_code=400, detail="File not ready for download")
        
        if not os.path.exists(file.output_path):
            raise HTTPException(status_code=404, detail="Output file not found")
        
        download_name = sanitize_filename(Path(file.original_name).stem) + ".pdf"
        
        with open(file.output_path, "rb") as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{download_name}\"",
                "Content-Length": str(len(content)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    
    @app.get("/api/tasks/{task_id}/preview/{file_id}")
    async def preview_file(task_id: str, file_id: str):
        task = conversion_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        file = next((f for f in task.files if f.id == file_id), None)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file.status != FileStatus.COMPLETED or not file.output_path:
            raise HTTPException(status_code=400, detail="File not ready for preview")
        
        if not os.path.exists(file.output_path):
            raise HTTPException(status_code=404, detail="Output file not found")
        
        with open(file.output_path, "rb") as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline",
                "Content-Length": str(len(content)),
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )
    
    @app.delete("/api/tasks/{task_id}")
    async def delete_task(task_id: str):
        success = conversion_manager.cleanup_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    
    @app.get("/api/health")
    async def health_check():
        return {"status": "healthy", "service": "pdfitdown-web"}
    
    @app.post("/api/features/{feature_type}/tasks/create", response_model=dict)
    async def create_feature_task(feature_type: FeatureType):
        task = feature_manager.create_task(feature_type)
        return {"task_id": task.id, "feature_type": feature_type}
    
    @app.post("/api/features/tasks/{task_id}/upload", response_model=UploadResponse)
    async def upload_feature_file(
        task_id: str,
        file: UploadFile = File(...)
    ):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        file_content = await file.read()
        file_size = len(file_content)
        
        uploaded_file = feature_manager.add_file_to_task(
            task_id=task_id,
            original_name=file.filename or "unnamed_file",
            file_content=file_content,
            file_size=file_size
        )
        
        if not uploaded_file:
            raise HTTPException(status_code=500, detail="Failed to upload file")
        
        return UploadResponse(
            task_id=task_id,
            file_id=uploaded_file.id,
            filename=uploaded_file.original_name,
            status=uploaded_file.status
        )
    
    @app.get("/api/features/tasks/{task_id}/status", response_model=FeatureTaskResponse)
    async def get_feature_task_status(task_id: str):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return FeatureTaskResponse(
            task_id=task.id,
            feature_type=task.feature_type,
            status=task.status,
            total_files=len(task.files),
            completed_count=task.completed_count,
            failed_count=task.failed_count,
            progress=task.progress,
            total_progress=task.progress,
            files=task.files,
            output_files=task.output_files,
            outputs=task.output_files,
            error_message=task.error_message
        )
    
    @app.post("/api/features/tasks/{task_id}/reorder")
    async def reorder_files(
        task_id: str,
        order: List[int] = Body(..., embed=True)
    ):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.status == TaskStatus.PROCESSING:
            raise HTTPException(status_code=400, detail="Cannot reorder files while processing")
        
        if len(order) != len(task.files):
            raise HTTPException(status_code=400, detail="Order list length must match number of files")
        
        new_files = []
        for idx in order:
            if idx < 0 or idx >= len(task.files):
                raise HTTPException(status_code=400, detail=f"Invalid order index: {idx}")
            new_files.append(task.files[idx])
        
        task.files = new_files
        return {"message": "Files reordered successfully", "order": order}
    
    @app.get("/api/features/tasks/{task_id}/pdf-info", response_model=PdfInfoResponse)
    async def get_pdf_info(task_id: str):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if len(task.files) != 1:
            raise HTTPException(status_code=400, detail="PDF info requires exactly 1 file")
        
        file = task.files[0]
        upload_path = getattr(file, '_upload_path', None)
        if not upload_path or not os.path.exists(upload_path):
            raise HTTPException(status_code=404, detail="Uploaded file not found")
        
        try:
            from .models import PageSize
            info = feature_manager.get_pdf_info(upload_path)
            
            page_size_obj = None
            if info.get("page_size"):
                page_size_data = info["page_size"]
                if isinstance(page_size_data, dict):
                    page_size_obj = PageSize(
                        width=float(page_size_data.get("width", 0)),
                        height=float(page_size_data.get("height", 0))
                    )
            
            return PdfInfoResponse(
                page_count=info["page_count"],
                page_size=page_size_obj,
                file_size=info["file_size"],
                pages=info.get("pages", []),
                filename=info.get("filename")
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get PDF info: {str(e)}")
    
    @app.post("/api/features/tasks/{task_id}/merge")
    async def start_merge(
        task_id: str,
        background_tasks: BackgroundTasks,
        order: Optional[List[int]] = Body(None, embed=True)
    ):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if len(task.files) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 PDF files to merge")
        
        if task.status == TaskStatus.PROCESSING:
            raise HTTPException(status_code=400, detail="Task is already processing")
        
        async def run_merge():
            await feature_manager.merge_pdfs(task_id, order)
        
        background_tasks.add_task(run_merge)
        
        return {
            "task_id": task_id,
            "feature_type": "merge",
            "status": "processing",
            "message": "Merge started"
        }
    
    @app.post("/api/features/tasks/{task_id}/split")
    async def start_split(
        task_id: str,
        background_tasks: BackgroundTasks,
        split_request: SplitRequest
    ):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if len(task.files) != 1:
            raise HTTPException(status_code=400, detail="Split requires exactly 1 PDF file")
        
        if task.status == TaskStatus.PROCESSING:
            raise HTTPException(status_code=400, detail="Task is already processing")
        
        async def run_split():
            await feature_manager.split_pdf(
                task_id=task_id,
                mode=split_request.mode,
                ranges=split_request.ranges,
                pages=split_request.pages,
                every_n=split_request.every_n,
                output_prefix=split_request.output_prefix
            )
        
        background_tasks.add_task(run_split)
        
        return {
            "task_id": task_id,
            "feature_type": "split",
            "status": "processing",
            "message": "Split started"
        }
    
    @app.post("/api/features/tasks/{task_id}/compress")
    async def start_compress(
        task_id: str,
        background_tasks: BackgroundTasks,
        compress_request: CompressRequest
    ):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if len(task.files) != 1:
            raise HTTPException(status_code=400, detail="Compress requires exactly 1 PDF file")
        
        if task.status == TaskStatus.PROCESSING:
            raise HTTPException(status_code=400, detail="Task is already processing")
        
        async def run_compress():
            await feature_manager.compress_pdf(task_id, compress_request.level)
        
        background_tasks.add_task(run_compress)
        
        return {
            "task_id": task_id,
            "feature_type": "compress",
            "status": "processing",
            "message": f"Compression started with {compress_request.level} level"
        }
    
    @app.get("/api/features/tasks/{task_id}/download/zip")
    async def download_feature_zip(task_id: str):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if task.status not in [TaskStatus.COMPLETED, TaskStatus.PARTIAL_FAILED]:
            raise HTTPException(status_code=400, detail="Task not completed")
        
        if not task.output_files:
            raise HTTPException(status_code=400, detail="No output files")
        
        if not task.zip_path:
            zip_path = feature_manager.create_zip(task_id)
            if not zip_path:
                raise HTTPException(
                    status_code=400, 
                    detail="No completed files to zip"
                )
        else:
            zip_path = task.zip_path
        
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="Zip file not found")
        
        zip_filename = f"{task.feature_type}_{task_id[:8]}.zip"
        
        with open(zip_path, "rb") as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=\"{zip_filename}\"",
                "Content-Length": str(len(content)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    
    @app.get("/api/features/tasks/{task_id}/download/{output_id}")
    async def download_feature_file(task_id: str, output_id: str):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        output_file = next((f for f in task.output_files if f.id == output_id), None)
        if not output_file:
            raise HTTPException(status_code=404, detail="Output file not found")
        
        if not output_file.output_path or not os.path.exists(output_file.output_path):
            raise HTTPException(status_code=404, detail="Output file not found")
        
        download_name = sanitize_filename(output_file.filename)
        
        with open(output_file.output_path, "rb") as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{download_name}\"",
                "Content-Length": str(len(content)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    
    @app.get("/api/features/tasks/{task_id}/preview/{output_id}")
    async def preview_feature_file(task_id: str, output_id: str):
        task = feature_manager.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        output_file = next((f for f in task.output_files if f.id == output_id), None)
        if not output_file:
            raise HTTPException(status_code=404, detail="Output file not found")
        
        if not output_file.output_path or not os.path.exists(output_file.output_path):
            raise HTTPException(status_code=404, detail="Output file not found")
        
        with open(output_file.output_path, "rb") as f:
            content = f.read()
        
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline",
                "Content-Length": str(len(content)),
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )
    
    @app.delete("/api/features/tasks/{task_id}")
    async def delete_feature_task(task_id: str):
        success = feature_manager.cleanup_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    
    return app


app = create_app()
