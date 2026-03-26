from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.config import settings
from app.schemas.documents import (
    DocumentChunkResponse,
    EmbeddingBuildResponse,
    IngestDocumentResponse,
    ListDocumentsResponse,
    SearchDocumentMatchResponse,
    SearchDocumentsResponse,
    SemanticSearchMatchResponse,
    SemanticSearchResponse,
    StoredDocumentResponse,
)
from app.services.document_store_service import DocumentStoreService
from app.services.embedding_service import EmbeddingService
from app.services.ingest_service import IngestService
from app.services.semantic_search_service import SemanticSearchService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/ingest", response_model=IngestDocumentResponse)
async def ingest_document(file: UploadFile = File(...)) -> IngestDocumentResponse:
    IngestService.validate_file(file)
    content = await IngestService.read_file_content(file)

    safe_file_name = Path(file.filename).name
    saved_path, chunks = IngestService.ingest_text(
        file_name=safe_file_name,
        content=content,
    )

    record = DocumentStoreService.create_document_record(
        file_name=safe_file_name,
        file_type=Path(safe_file_name).suffix.lower(),
        saved_path=saved_path,
        total_characters=len(content),
        chunks=chunks,
    )
    DocumentStoreService.append_document(record)

    return IngestDocumentResponse(
        document_id=record["document_id"],
        file_name=safe_file_name,
        file_type=record["file_type"],
        saved_path=str(saved_path),
        total_characters=record["total_characters"],
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        total_chunks=len(chunks),
        chunks=[DocumentChunkResponse(**chunk) for chunk in chunks],
    )


@router.get("", response_model=ListDocumentsResponse)
def list_documents() -> ListDocumentsResponse:
    documents = DocumentStoreService.list_documents()

    return ListDocumentsResponse(
        total_documents=len(documents),
        documents=[StoredDocumentResponse(**doc) for doc in documents],
    )


@router.get("/search", response_model=SearchDocumentsResponse)
def search_documents(
    query: str = Query(..., min_length=1, description="Keyword to search in document chunks"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
) -> SearchDocumentsResponse:
    normalized_query = query.strip()
    if not normalized_query:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    matches = DocumentStoreService.search_documents(
        query=normalized_query,
        limit=limit,
    )

    return SearchDocumentsResponse(
        query=normalized_query,
        total_matches=len(matches),
        matches=[SearchDocumentMatchResponse(**match) for match in matches],
    )


@router.post("/embeddings/rebuild", response_model=EmbeddingBuildResponse)
def rebuild_embeddings() -> EmbeddingBuildResponse:
    try:
        result = EmbeddingService.rebuild_embeddings()
        return EmbeddingBuildResponse(
            total_embedding_records=result["total_embedding_records"],
            embedding_model=settings.embedding_model,
            documents_processed=result["documents_processed"],
            chunks_processed=result["chunks_processed"],
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/semantic-search", response_model=SemanticSearchResponse)
def semantic_search(
    query: str = Query(..., min_length=1, description="Semantic query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results"),
) -> SemanticSearchResponse:
    normalized_query = query.strip()
    if not normalized_query:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    matches = SemanticSearchService.search(
        query=normalized_query,
        limit=limit,
    )

    return SemanticSearchResponse(
        query=normalized_query,
        total_matches=len(matches),
        matches=[SemanticSearchMatchResponse(**match) for match in matches],
    )