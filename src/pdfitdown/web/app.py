import os
from pathlib import Path
from typing import Optional
import logging

from fastapi import (
    FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks,
    Request
)
from fastapi.responses import (
    HTMLResponse, FileResponse, JSONResponse, StreamingResponse
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import (
    UploadResponse, TaskStatusResponse, StartConversionRequest,
    DownloadInfo, FileStatus, TaskStatus
)
from .manager import conversion_manager

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


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
        
        download_name = Path(file.original_name).stem + ".pdf"
        
        return FileResponse(
            path=file.output_path,
            media_type="application/pdf",
            filename=download_name
        )
    
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
        
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"converted_{task_id[:8]}.zip"
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
    
    return app


app = create_app()
