from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class DraftChecklistRequest(BaseModel):
    document_id: Optional[str] = Field(default=None, description="Indexed document ID")
    raw_text: Optional[str] = Field(default=None, description="Raw document text")

    @model_validator(mode="after")
    def validate_input(self):
        if not self.document_id and not self.raw_text:
            raise ValueError("Either document_id or raw_text must be provided")
        return self


class DraftChecklistResponse(BaseModel):
    document_id: Optional[str]
    happy_path: List[str]
    validation: List[str]
    edge_cases: List[str]