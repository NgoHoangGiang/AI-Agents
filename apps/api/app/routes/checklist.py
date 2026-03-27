from fastapi import APIRouter, HTTPException

from app.schemas.checklist import DraftChecklistRequest, DraftChecklistResponse
from app.services.checklist_service import ChecklistService

router = APIRouter(prefix="/draft-checklist", tags=["checklist"])


@router.post("", response_model=DraftChecklistResponse)
def draft_checklist(request: DraftChecklistRequest) -> DraftChecklistResponse:
    try:
        result = ChecklistService.draft(
            document_id=request.document_id,
            raw_text=request.raw_text,
        )
        return DraftChecklistResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc