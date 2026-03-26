from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentChunkResponse(BaseModel):
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    content: str = Field(..., description="Chunk content")
    start_char: int = Field(..., description="Start character index in original text")
    end_char: int = Field(..., description="End character index in original text")


class IngestDocumentResponse(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    saved_path: str
    total_characters: int
    chunk_size: int
    chunk_overlap: int
    total_chunks: int
    chunks: List[DocumentChunkResponse]


class StoredDocumentResponse(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    saved_path: str
    total_characters: int
    total_chunks: int
    uploaded_at: str


class SearchDocumentMatchResponse(BaseModel):
    document_id: str
    file_name: str
    chunk_index: int
    matched_text: str
    score: int


class SearchDocumentsResponse(BaseModel):
    query: str
    total_matches: int
    matches: List[SearchDocumentMatchResponse]


class ListDocumentsResponse(BaseModel):
    total_documents: int
    documents: List[StoredDocumentResponse]


class ErrorResponse(BaseModel):
    detail: str


class SearchQueryParams(BaseModel):
    query: str
    limit: Optional[int] = 10