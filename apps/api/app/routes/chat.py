from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty")

    result = ChatService.ask(
        question=question,
        top_k=request.top_k,
    )

    return ChatResponse(**result)