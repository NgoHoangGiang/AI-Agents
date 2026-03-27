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

    NOISE_PATTERNS = [
        r"^#",
        r"^sample hld$",
        r"^this is a simple internal project document\.?$",
        r"^business rules:?$",
        r"^acceptance criteria:?$",
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
        cleaned_lines: List[str] = []

        for line in raw_lines:
            normalized = line.strip()
            if not normalized:
                continue

            normalized = re.sub(r"\s+", " ", normalized)
            cleaned_lines.append(normalized)

        return cleaned_lines

    @staticmethod
    def clean_line(line: str) -> str:
        cleaned = line.strip()
        cleaned = cleaned.lstrip("- ").strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.replace("#", "").strip()

        if cleaned and cleaned[-1] not in ".!?":
            cleaned += "."

        return cleaned

    @staticmethod
    def is_noise_line(line: str) -> bool:
        normalized = line.strip().lower()
        if not normalized:
            return True

        for pattern in SummarizeService.NOISE_PATTERNS:
            if re.match(pattern, normalized, flags=re.IGNORECASE):
                return True

        return False

    @staticmethod
    def score_line(line: str) -> int:
        lowered = line.lower()
        score = 0

        if "segment name" in lowered:
            score += 4
        if "search" in lowered:
            score += 3
        if "case-insensitive" in lowered:
            score += 3
        if "realtime" in lowered or "real-time" in lowered:
            score += 3
        if "must" in lowered or "required" in lowered:
            score += 3
        if "open new tab" in lowered:
            score += 3
        if line.startswith("-"):
            score += 1

        return score

    @staticmethod
    def prepare_lines(text: str) -> List[str]:
        raw_lines = SummarizeService.split_lines(text)
        prepared: List[str] = []

        for line in raw_lines:
            cleaned = SummarizeService.clean_line(line)

            if SummarizeService.is_noise_line(cleaned):
                continue

            prepared.append(cleaned)

        return prepared

    @staticmethod
    def build_summary(lines: List[str], max_lines: int = 3) -> str:
        if not lines:
            return "No clear summary could be generated from the provided document."

        scored = [{"line": line, "score": SummarizeService.score_line(line)} for line in lines]
        scored.sort(key=lambda item: item["score"], reverse=True)

        selected: List[str] = []
        seen = set()

        for item in scored:
            line = item["line"]
            key = line.lower()

            if key in seen:
                continue

            selected.append(line)
            seen.add(key)

            if len(selected) >= max_lines:
                break

        return " ".join(selected)

    @staticmethod
    def extract_key_points(lines: List[str], limit: int = 5) -> List[str]:
        scored = [{"line": line, "score": SummarizeService.score_line(line)} for line in lines]
        scored.sort(key=lambda item: item["score"], reverse=True)

        key_points: List[str] = []
        seen = set()

        for item in scored:
            line = item["line"]
            key = line.lower()

            if key in seen:
                continue

            key_points.append(line)
            seen.add(key)

            if len(key_points) >= limit:
                break

        return key_points

    @staticmethod
    def extract_business_rules(lines: List[str], limit: int = 5) -> List[str]:
        business_rules: List[str] = []
        seen = set()

        for line in lines:
            lowered = line.lower()

            if any(hint in lowered for hint in SummarizeService.BUSINESS_RULE_HINTS):
                key = line.lower()
                if key not in seen:
                    business_rules.append(line)
                    seen.add(key)

            if len(business_rules) >= limit:
                break

        return business_rules

    @staticmethod
    def extract_open_questions(lines: List[str], limit: int = 5) -> List[str]:
        open_questions: List[str] = []
        seen = set()

        for line in lines:
            lowered = line.lower()

            if any(hint in lowered for hint in SummarizeService.OPEN_QUESTION_HINTS):
                key = line.lower()
                if key not in seen:
                    open_questions.append(line)
                    seen.add(key)

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

        prepared_lines = SummarizeService.prepare_lines(text)

        return {
            "document_id": document_id,
            "summary": SummarizeService.build_summary(prepared_lines),
            "key_points": SummarizeService.extract_key_points(prepared_lines),
            "business_rules": SummarizeService.extract_business_rules(prepared_lines),
            "open_questions": SummarizeService.extract_open_questions(prepared_lines),
        }