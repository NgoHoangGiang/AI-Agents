import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.config import settings


class DocumentStoreService:
    @staticmethod
    def _ensure_metadata_file() -> None:
        if not settings.metadata_file_path.exists():
            settings.metadata_file_path.write_text("[]", encoding="utf-8")

    @staticmethod
    def load_documents() -> List[Dict[str, Any]]:
        DocumentStoreService._ensure_metadata_file()
        content = settings.metadata_file_path.read_text(encoding="utf-8").strip()

        if not content:
            return []

        try:
            data = json.loads(content)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    @staticmethod
    def save_documents(documents: List[Dict[str, Any]]) -> None:
        settings.metadata_file_path.write_text(
            json.dumps(documents, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def create_document_record(
        file_name: str,
        file_type: str,
        saved_path: Path,
        total_characters: int,
        chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "document_id": str(uuid4()),
            "file_name": file_name,
            "file_type": file_type,
            "saved_path": str(saved_path),
            "total_characters": total_characters,
            "total_chunks": len(chunks),
            "uploaded_at": datetime.now(UTC).isoformat(),
            "chunks": chunks,
        }

    @staticmethod
    def append_document(record: Dict[str, Any]) -> None:
        documents = DocumentStoreService.load_documents()
        documents.append(record)
        DocumentStoreService.save_documents(documents)

    @staticmethod
    def list_documents() -> List[Dict[str, Any]]:
        documents = DocumentStoreService.load_documents()
        return [
            {
                "document_id": doc["document_id"],
                "file_name": doc["file_name"],
                "file_type": doc["file_type"],
                "saved_path": doc["saved_path"],
                "total_characters": doc["total_characters"],
                "total_chunks": doc["total_chunks"],
                "uploaded_at": doc["uploaded_at"],
            }
            for doc in documents
        ]

    @staticmethod
    def search_documents(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            return []

        documents = DocumentStoreService.load_documents()
        matches: List[Dict[str, Any]] = []

        for doc in documents:
            for chunk in doc.get("chunks", []):
                content = chunk.get("content", "")
                lowered = content.lower()

                if normalized_query in lowered:
                    score = lowered.count(normalized_query)

                    matches.append(
                        {
                            "document_id": doc["document_id"],
                            "file_name": doc["file_name"],
                            "chunk_index": chunk["chunk_index"],
                            "matched_text": content,
                            "score": score,
                        }
                    )

        matches.sort(key=lambda item: item["score"], reverse=True)
        return matches[:limit]