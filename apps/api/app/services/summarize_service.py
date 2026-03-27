import re
from typing import Dict, List, Optional

from app.services.document_store_service import DocumentStoreService


class SummarizeService:
    BUSINESS_RULE_HINTS = [
        "must",
        "should",
        "required",
        "mandatory",
        "case-insensitive",
        "realtime",
        "real-time",
        "not allowed",
        "open new tab",
    ]

    OPEN_QUESTION_HINTS = [
        "todo",
        "tbd",
        "open question",
        "pending",
        "unclear",
        "?",
    ]

    @staticmethod
    def get_document_text(document_id: str) -> Optional[str]:
        documents = DocumentStoreService.load_documents()

        for doc in documents:
            if doc["document_id"] == document_id:
                chunks = doc.get("chunks", [])
                return "\n".join(chunk.get("content", "") for chunk in chunks).strip()

        return None

    @staticmethod
    def split_lines(text: str) -> List[str]:
        raw_lines = text.splitlines()
        cleaned_lines = []

        for line in raw_lines:
            normalized = line.strip()
            if not normalized:
                continue

            normalized = re.sub(r"\s+", " ", normalized)
            cleaned_lines.append(normalized)

        return cleaned_lines

    @staticmethod
    def build_summary(lines: List[str], max_lines: int = 4) -> str:
        filtered = []
        for line in lines:
            lowered = line.lower()

            if lowered.startswith("#"):
                continue
            if lowered in {"business rules:", "acceptance criteria:"}:
                continue

            filtered.append(line)

            if len(filtered) >= max_lines:
                break

        if not filtered:
            return "No clear summary could be generated from the provided document."

        return " ".join(filtered)

    @staticmethod
    def extract_key_points(lines: List[str], limit: int = 5) -> List[str]:
        key_points: List[str] = []

        for line in lines:
            lowered = line.lower()

            if lowered.startswith("#"):
                continue

            if line.startswith("-") or ":" in line or len(line.split()) >= 4:
                point = line.lstrip("- ").strip()
                if point not in key_points:
                    key_points.append(point)

            if len(key_points) >= limit:
                break

        return key_points

    @staticmethod
    def extract_business_rules(lines: List[str], limit: int = 5) -> List[str]:
        business_rules: List[str] = []

        for line in lines:
            normalized = line.lstrip("- ").strip()
            lowered = normalized.lower()

            if any(hint in lowered for hint in SummarizeService.BUSINESS_RULE_HINTS):
                if normalized not in business_rules:
                    business_rules.append(normalized)

            if len(business_rules) >= limit:
                break

        return business_rules

    @staticmethod
    def extract_open_questions(lines: List[str], limit: int = 5) -> List[str]:
        open_questions: List[str] = []

        for line in lines:
            normalized = line.lstrip("- ").strip()
            lowered = normalized.lower()

            if any(hint in lowered for hint in SummarizeService.OPEN_QUESTION_HINTS):
                if normalized not in open_questions:
                    open_questions.append(normalized)

            if len(open_questions) >= limit:
                break

        return open_questions

    @staticmethod
    def summarize(document_id: Optional[str] = None, raw_text: Optional[str] = None) -> Dict:
        text = raw_text.strip() if raw_text else None

        if document_id:
            text = SummarizeService.get_document_text(document_id=document_id)
            if text is None:
                raise ValueError("Document not found")

        if not text:
            raise ValueError("No text available to summarize")

        lines = SummarizeService.split_lines(text)

        return {
            "document_id": document_id,
            "summary": SummarizeService.build_summary(lines),
            "key_points": SummarizeService.extract_key_points(lines),
            "business_rules": SummarizeService.extract_business_rules(lines),
            "open_questions": SummarizeService.extract_open_questions(lines),
        }