from pathlib import Path

from fastapi import APIRouter, UploadFile, File

from app.config import settings
from app.schemas.documents import IngestDocumentResponse, DocumentChunkResponse
from app.services.ingest_service import IngestService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/ingest", response_model=IngestDocumentResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestDocumentResponse:
    extension = IngestService.validate_file(file)
    content = await IngestService.read_file_content(file)

    safe_file_name = Path(file.filename).name
    saved_path, chunks = IngestService.ingest_text(
        file_name=safe_file_name,
        extension=extension,
        content=content,
    )

    return IngestDocumentResponse(
        file_name=safe_file_name,
        file_type=extension,
        saved_path=str(saved_path),
        total_characters=len(content),
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        total_chunks=len(chunks),
        chunks=[DocumentChunkResponse(**chunk) for chunk in chunks],
    )