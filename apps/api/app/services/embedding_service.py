import json
from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer

from app.config import settings
from app.services.document_store_service import DocumentStoreService


class EmbeddingService:
    _model: SentenceTransformer | None = None

    @staticmethod
    def _get_model() -> SentenceTransformer:
        if EmbeddingService._model is None:
            EmbeddingService._model = SentenceTransformer(settings.embedding_model)
        return EmbeddingService._model

    @staticmethod
    def _ensure_embeddings_file() -> None:
        if not settings.embeddings_file_path.exists():
            settings.embeddings_file_path.write_text("[]", encoding="utf-8")

    @staticmethod
    def load_embeddings() -> List[Dict[str, Any]]:
        EmbeddingService._ensure_embeddings_file()
        content = settings.embeddings_file_path.read_text(encoding="utf-8").strip()

        if not content:
            return []

        try:
            data = json.loads(content)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    @staticmethod
    def save_embeddings(records: List[Dict[str, Any]]) -> None:
        settings.embeddings_file_path.write_text(
            json.dumps(records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def create_embedding(text: str) -> List[float]:
        model = EmbeddingService._get_model()
        vector = model.encode(text, convert_to_numpy=True)
        return vector.tolist()

    @staticmethod
    def rebuild_embeddings() -> Dict[str, int]:
        documents = DocumentStoreService.load_documents()
        records: List[Dict[str, Any]] = []

        documents_processed = 0
        chunks_processed = 0

        for doc in documents:
            documents_processed += 1

            for chunk in doc.get("chunks", []):
                content = chunk.get("content", "").strip()
                if not content:
                    continue

                vector = EmbeddingService.create_embedding(content)

                records.append(
                    {
                        "document_id": doc["document_id"],
                        "file_name": doc["file_name"],
                        "chunk_index": chunk["chunk_index"],
                        "content": content,
                        "embedding": vector,
                    }
                )
                chunks_processed += 1

        EmbeddingService.save_embeddings(records)

        return {
            "total_embedding_records": len(records),
            "documents_processed": documents_processed,
            "chunks_processed": chunks_processed,
        }

    @staticmethod
    def create_query_embedding(query: str) -> List[float]:
        return EmbeddingService.create_embedding(query)