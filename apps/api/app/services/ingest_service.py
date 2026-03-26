from pathlib import Path
from typing import Tuple, List, Dict

from fastapi import HTTPException, UploadFile

from app.config import settings
from app.utils.chunking import chunk_text


class IngestService:
    ALLOWED_EXTENSIONS = {".md", ".txt", ".sql"}

    @staticmethod
    def validate_file(upload_file: UploadFile) -> str:
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="Uploaded file must have a filename")

        extension = Path(upload_file.filename).suffix.lower()

        if extension not in IngestService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {extension}. Allowed: {sorted(IngestService.ALLOWED_EXTENSIONS)}",
            )

        return extension

    @staticmethod
    async def read_file_content(upload_file: UploadFile) -> str:
        file_bytes = await upload_file.read()

        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_upload_size_mb} MB",
            )

        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail="File must be UTF-8 encoded text",
            ) from exc

    @staticmethod
    def normalize_text(content: str) -> str:
        return content.replace("\r\n", "\n").replace("\r", "\n").strip()

    @staticmethod
    def save_raw_file(file_name: str, content: str) -> Path:
        save_path = settings.raw_data_dir / file_name
        save_path.write_text(content, encoding="utf-8")
        return save_path

    @staticmethod
    def ingest_text(file_name: str, content: str) -> Tuple[Path, List[Dict]]:
        normalized_content = IngestService.normalize_text(content)

        saved_path = IngestService.save_raw_file(
            file_name=file_name,
            content=normalized_content,
        )

        chunks = chunk_text(
            text=normalized_content,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        return saved_path, chunks