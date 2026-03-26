from typing import Dict, List

from app.services.semantic_search_service import SemanticSearchService


class ChatService:
    @staticmethod
    def retrieve_relevant_chunks(question: str, top_k: int = 3) -> List[Dict]:
        return SemanticSearchService.search(query=question, limit=top_k)

    @staticmethod
    def build_grounded_answer(question: str, matches: List[Dict]) -> str:
        if not matches:
            return (
                "I could not find relevant information in the indexed documents "
                "to answer this question."
            )

        lines: List[str] = []
        lines.append(f"Question: {question}")
        lines.append("")
        lines.append("Answer based on retrieved documents:")
        lines.append("")

        for idx, match in enumerate(matches, start=1):
            file_name = match["file_name"]
            chunk_index = match["chunk_index"]
            content = match["content"].strip()

            lines.append(f"{idx}. Source: {file_name} | chunk {chunk_index}")
            lines.append(content)
            lines.append("")

        lines.append(
            "Note: this is a grounded draft answer built directly from retrieved "
            "document chunks. A later step can replace this with LLM-generated synthesis."
        )

        return "\n".join(lines)

    @staticmethod
    def ask(question: str, top_k: int = 3) -> Dict:
        matches = ChatService.retrieve_relevant_chunks(question=question, top_k=top_k)
        answer = ChatService.build_grounded_answer(question=question, matches=matches)

        citations = [
            {
                "document_id": match["document_id"],
                "file_name": match["file_name"],
                "chunk_index": match["chunk_index"],
                "similarity": match["similarity"],
            }
            for match in matches
        ]

        used_chunks = [
            {
                "document_id": match["document_id"],
                "file_name": match["file_name"],
                "chunk_index": match["chunk_index"],
                "content": match["content"],
                "similarity": match["similarity"],
            }
            for match in matches
        ]

        return {
            "question": question,
            "answer": answer,
            "total_used_chunks": len(matches),
            "citations": citations,
            "used_chunks": used_chunks,
        }