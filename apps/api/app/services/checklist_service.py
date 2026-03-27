import re
from typing import Dict, List, Optional

from app.services.document_store_service import DocumentStoreService


class ChecklistService:
    NOISE_PATTERNS = [
        r"^#",
        r"^sample hld$",
        r"^business rules:?$",
        r"^acceptance criteria:?$",
        r"^this is a simple internal project document\.?$",
    ]

    HAPPY_PATH_HINTS = [
        "user can",
        "system returns",
        "system displays",
        "user can create",
        "user can view",
        "user can submit",
        "search by",
    ]

    VALIDATION_HINTS = [
        "case-insensitive",
        "required",
        "mandatory",
        "must",
        "not allowed",
        "format",
        "validate",
        "reject",
        "open new tab",
    ]

    EDGE_CASE_HINTS = [
        "realtime",
        "real-time",
        "not found",
        "empty",
        "no result",
        "duplicate",
        "past date",
        "uppercase",
        "lowercase",
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
        cleaned = cleaned.replace("#", "").strip()
        cleaned = re.sub(r"\s+", " ", cleaned)

        if cleaned and cleaned[-1] not in ".!?":
            cleaned += "."

        return cleaned

    @staticmethod
    def is_noise_line(line: str) -> bool:
        normalized = line.strip().lower()
        if not normalized:
            return True

        for pattern in ChecklistService.NOISE_PATTERNS:
            if re.match(pattern, normalized, flags=re.IGNORECASE):
                return True

        return False

    @staticmethod
    def prepare_lines(text: str) -> List[str]:
        raw_lines = ChecklistService.split_lines(text)
        prepared: List[str] = []

        for line in raw_lines:
            cleaned = ChecklistService.clean_line(line)

            if ChecklistService.is_noise_line(cleaned):
                continue

            prepared.append(cleaned)

        return prepared

    @staticmethod
    def score_line(line: str) -> int:
        lowered = line.lower()
        score = 0

        if "segment name" in lowered:
            score += 4
        if "search" in lowered:
            score += 3
        if "case-insensitive" in lowered:
            score += 4
        if "open new tab" in lowered:
            score += 4
        if "realtime" in lowered or "real-time" in lowered:
            score += 3
        if "required" in lowered or "must" in lowered:
            score += 3
        if "reject" in lowered:
            score += 3
        if "user can" in lowered:
            score += 3
        if "system returns" in lowered or "system displays" in lowered:
            score += 3

        return score

    @staticmethod
    def to_check_sentence(line: str) -> str:
        normalized = line.strip()

        replacements = [
            (r"^User can ", "Verify the user can "),
            (r"^System returns ", "Verify the system returns "),
            (r"^System displays ", "Verify the system displays "),
            (r"^System should ", "Verify the system should "),
            (r"^System ", "Verify the system "),
            (r"^Search is ", "Verify search is "),
            (r"^Onclick must ", "Verify onclick actions must "),
            (r"^User must ", "Verify the user must "),
            (r"^Booking code format is ", "Verify booking code format is "),
        ]

        for pattern, replacement in replacements:
            if re.match(pattern, normalized, flags=re.IGNORECASE):
                converted = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
                return ChecklistService.ensure_sentence_punctuation(converted)

        if not normalized.lower().startswith("verify"):
            converted = f"Verify {normalized[0].lower()}{normalized[1:]}" if len(normalized) > 1 else f"Verify {normalized.lower()}"
            return ChecklistService.ensure_sentence_punctuation(converted)

        return ChecklistService.ensure_sentence_punctuation(normalized)

    @staticmethod
    def ensure_sentence_punctuation(text: str) -> str:
        text = text.strip()
        if text and text[-1] not in ".!?":
            text += "."
        return text

    @staticmethod
    def classify_line(line: str) -> str:
        lowered = line.lower()

        if any(keyword in lowered for keyword in ChecklistService.VALIDATION_HINTS):
            return "validation"

        if any(keyword in lowered for keyword in ChecklistService.HAPPY_PATH_HINTS):
            return "happy_path"

        if any(keyword in lowered for keyword in ChecklistService.EDGE_CASE_HINTS):
            return "edge_cases"

        return "unknown"

    @staticmethod
    def build_happy_path(lines: List[str], limit: int = 5) -> List[str]:
        candidates = []

        for line in lines:
            if ChecklistService.classify_line(line) == "happy_path":
                candidates.append(
                    {
                        "line": ChecklistService.to_check_sentence(line),
                        "score": ChecklistService.score_line(line),
                    }
                )

        candidates.sort(key=lambda item: item["score"], reverse=True)

        results: List[str] = []
        seen = set()

        for item in candidates:
            line = item["line"]
            key = line.lower()

            if key in seen:
                continue

            results.append(line)
            seen.add(key)

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def build_validation(lines: List[str], limit: int = 5) -> List[str]:
        candidates = []

        for line in lines:
            if ChecklistService.classify_line(line) == "validation":
                candidates.append(
                    {
                        "line": ChecklistService.to_check_sentence(line),
                        "score": ChecklistService.score_line(line),
                    }
                )

        candidates.sort(key=lambda item: item["score"], reverse=True)

        results: List[str] = []
        seen = set()

        for item in candidates:
            line = item["line"]
            key = line.lower()

            if key in seen:
                continue

            results.append(line)
            seen.add(key)

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def infer_edge_cases(lines: List[str]) -> List[str]:
        inferred: List[str] = []
        lowered_joined = " ".join(lines).lower()

        if "search" in lowered_joined:
            inferred.append("Verify the system shows the correct behavior when no segment name matches the search query.")
            inferred.append("Verify the system handles empty search input correctly.")

        if "case-insensitive" in lowered_joined:
            inferred.append("Verify search still returns the correct result when the user enters uppercase and lowercase variations.")

        if "realtime" in lowered_joined or "real-time" in lowered_joined:
            inferred.append("Verify repeated typing updates the result correctly without breaking the search flow.")

        if "open new tab" in lowered_joined:
            inferred.append("Verify clicking the related action opens exactly one new tab.")

        if "reject past dates" in lowered_joined or "past date" in lowered_joined:
            inferred.append("Verify the system rejects past dates and shows the expected validation behavior.")

        return inferred

    @staticmethod
    def build_edge_cases(lines: List[str], limit: int = 5) -> List[str]:
        results: List[str] = []
        seen = set()

        for item in ChecklistService.infer_edge_cases(lines):
            key = item.lower()
            if key not in seen:
                results.append(ChecklistService.ensure_sentence_punctuation(item))
                seen.add(key)

            if len(results) >= limit:
                return results

        for line in lines:
            if ChecklistService.classify_line(line) == "edge_cases":
                item = ChecklistService.to_check_sentence(line)
                key = item.lower()

                if key not in seen:
                    results.append(item)
                    seen.add(key)

                if len(results) >= limit:
                    break

        return results

    @staticmethod
    def draft(document_id: Optional[str] = None, raw_text: Optional[str] = None) -> Dict:
        text = raw_text.strip() if raw_text else None

        if document_id:
            text = ChecklistService.get_document_text(document_id=document_id)
            if text is None:
                raise ValueError("Document not found")

        if not text:
            raise ValueError("No text available to draft checklist")

        prepared_lines = ChecklistService.prepare_lines(text)

        return {
            "document_id": document_id,
            "happy_path": ChecklistService.build_happy_path(prepared_lines),
            "validation": ChecklistService.build_validation(prepared_lines),
            "edge_cases": ChecklistService.build_edge_cases(prepared_lines),
        }