from fastapi import APIRouter, HTTPException

from app.schemas.summarize import SummarizeDocumentRequest, SummarizeDocumentResponse
from app.services.summarize_service import SummarizeService

router = APIRouter(prefix="/summarize-document", tags=["summarize"])


@router.post("", response_model=SummarizeDocumentResponse)
def summarize_document(request: SummarizeDocumentRequest) -> SummarizeDocumentResponse:
    try:
        result = SummarizeService.summarize(
            document_id=request.document_id,
            raw_text=request.raw_text,
        )
        return SummarizeDocumentResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc