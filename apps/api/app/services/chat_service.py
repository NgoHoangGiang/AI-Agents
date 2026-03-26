import re
from typing import Dict, List

from app.services.semantic_search_service import SemanticSearchService


class ChatService:
    NOISE_PATTERNS = [
        r"^#",
        r"^this is a simple internal project document\.?$",
        r"^business rules:?$",
        r"^acceptance criteria:?$",
        r"^sample hld$",
    ]

    @staticmethod
    def retrieve_relevant_chunks(question: str, top_k: int = 3) -> List[Dict]:
        return SemanticSearchService.search(query=question, limit=top_k)

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        normalized = text.replace("\n", " ").strip()
        if not normalized:
            return []

        parts = re.split(r"(?<=[.!?])\s+|\s*-\s+", normalized)
        sentences = [part.strip() for part in parts if part.strip()]
        return sentences

    @staticmethod
    def clean_sentence(sentence: str) -> str:
        cleaned = sentence.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.replace("#", "").strip()

        if cleaned and cleaned[-1] not in ".!?":
            cleaned += "."

        return cleaned

    @staticmethod
    def is_noise_sentence(sentence: str) -> bool:
        normalized = sentence.strip().lower()
        if not normalized:
            return True

        for pattern in ChatService.NOISE_PATTERNS:
            if re.match(pattern, normalized, flags=re.IGNORECASE):
                return True

        return False

    @staticmethod
    def score_sentence(question: str, sentence: str) -> int:
        question_words = {
            word.lower()
            for word in re.findall(r"\w+", question)
            if len(word) >= 3
        }
        sentence_words = {
            word.lower()
            for word in re.findall(r"\w+", sentence)
            if len(word) >= 3
        }

        overlap = question_words.intersection(sentence_words)
        score = len(overlap)

        lowered = sentence.lower()
        if "search" in lowered:
            score += 2
        if "segment name" in lowered:
            score += 3
        if "case-insensitive" in lowered:
            score += 2
        if "realtime" in lowered or "real time" in lowered:
            score += 2

        return score

    @staticmethod
    def extract_best_sentences(question: str, matches: List[Dict], max_sentences: int = 4) -> List[str]:
        scored_sentences: List[Dict] = []

        for match in matches:
            sentences = ChatService.split_into_sentences(match["content"])

            for sentence in sentences:
                cleaned = ChatService.clean_sentence(sentence)

                if ChatService.is_noise_sentence(cleaned):
                    continue

                score = ChatService.score_sentence(question, cleaned)

                scored_sentences.append(
                    {
                        "sentence": cleaned,
                        "score": score,
                        "similarity": match["similarity"],
                    }
                )

        scored_sentences.sort(
            key=lambda item: (item["score"], item["similarity"]),
            reverse=True,
        )

        selected: List[str] = []
        seen = set()

        for item in scored_sentences:
            sentence = item["sentence"].strip()
            if not sentence:
                continue

            key = sentence.lower()
            if key in seen:
                continue

            selected.append(sentence)
            seen.add(key)

            if len(selected) >= max_sentences:
                break

        return selected

    @staticmethod
    def synthesize_answer(question: str, sentences: List[str], best_similarity: float) -> str:
        if not sentences:
            return (
                "I found related document chunks, but I could not extract a clear answer "
                "from them."
            )

        question_lower = question.lower()

        if "segment" in question_lower and "search" in question_lower:
            search_rule = None
            case_rule = None
            realtime_rule = None

            for sentence in sentences:
                lowered = sentence.lower()
                if "segment name" in lowered:
                    search_rule = sentence
                elif "case-insensitive" in lowered:
                    case_rule = sentence
                elif "realtime" in lowered or "real time" in lowered:
                    realtime_rule = sentence

            ordered_parts = [part for part in [search_rule, case_rule, realtime_rule] if part]

            if ordered_parts:
                answer = " ".join(ordered_parts)
            else:
                answer = " ".join(sentences[:3])
        else:
            answer = " ".join(sentences[:3])

        if best_similarity < 0.2:
            answer += " This answer is based on weakly related document matches, so it may need manual review."

        return answer

    @staticmethod
    def build_grounded_answer(question: str, matches: List[Dict]) -> str:
        if not matches:
            return (
                "I could not find enough relevant information in the indexed documents "
                "to answer this question."
            )

        best_similarity = matches[0]["similarity"] if matches else 0.0
        best_sentences = ChatService.extract_best_sentences(question=question, matches=matches)
        return ChatService.synthesize_answer(
            question=question,
            sentences=best_sentences,
            best_similarity=best_similarity,
        )

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