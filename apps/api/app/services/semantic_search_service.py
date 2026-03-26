from typing import Any, Dict, List

import numpy as np

from app.services.embedding_service import EmbeddingService


class SemanticSearchService:
    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        a = np.array(vec_a, dtype=float)
        b = np.array(vec_b, dtype=float)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    @staticmethod
    def search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        records = EmbeddingService.load_embeddings()
        if not records:
            return []

        query_embedding = EmbeddingService.create_query_embedding(query)
        matches: List[Dict[str, Any]] = []

        for record in records:
            similarity = SemanticSearchService.cosine_similarity(
                query_embedding,
                record["embedding"],
            )

            matches.append(
                {
                    "document_id": record["document_id"],
                    "file_name": record["file_name"],
                    "chunk_index": record["chunk_index"],
                    "content": record["content"],
                    "similarity": round(similarity, 6),
                }
            )

        matches.sort(key=lambda item: item["similarity"], reverse=True)
        return matches[:limit]