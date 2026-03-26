from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of retrieved chunks")


class ChatCitation(BaseModel):
    document_id: str
    file_name: str
    chunk_index: int
    similarity: float


class ChatUsedChunk(BaseModel):
    document_id: str
    file_name: str
    chunk_index: int
    content: str
    similarity: float


class ChatResponse(BaseModel):
    question: str
    answer: str
    total_used_chunks: int
    citations: List[ChatCitation]
    used_chunks: List[ChatUsedChunk]