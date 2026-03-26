from typing import List

from pydantic import BaseModel, Field

class DocumentChunkResponse(BaseModel):
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    content: str = Field(..., description="Chunk content")
    start_char: int = Field(..., description="Start character index in original text")
    end_char: int = Field(..., description="End character index in original text")

class IngestDocumentResponse(BaseModel):
    file_name: str
    file_type: str
    saved_path: str
    total_characters: int
    chunk_size: int
    chunk_overlap: int
    total_chunks: int
    chunks: List[DocumentChunkResponse]