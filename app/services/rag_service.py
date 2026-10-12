from __future__ import annotations

from pathlib import Path

from app.config import get_settings


class RAGService:
    def __init__(self, persist_directory: str | None = None):
        self.settings = get_settings()
        self.persist_directory = Path(persist_directory or self.settings.CHROMA_PERSIST_DIRECTORY)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self._vector_store_available = False
        try:
            import chromadb  # type: ignore  # noqa: F401
            self._vector_store_available = True
        except Exception:
            self._vector_store_available = False

    def ingest_documents(self) -> list[str]:
        faq_dir = Path(__file__).resolve().parents[2] / "data" / "faq"
        documents: list[str] = []
        if faq_dir.exists():
            for file in sorted(faq_dir.glob("**/*.*")):
                text = file.read_text(encoding="utf-8", errors="ignore")
                if text.strip():
                    documents.append(text)
        return documents

    def retrieve_relevant_documents(self, query: str, product_id: str | None = None, limit: int = 3) -> list[dict]:
        docs = self.ingest_documents()
        if not docs:
            return []
        query_terms = {term.lower() for term in query.lower().split() if term.strip()}
        scored = []
        for idx, doc in enumerate(docs):
            text = doc.lower()
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                scored.append({"score": score, "content": doc, "source": f"faq_{idx}.txt"})
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:limit]

    def answer_question(self, question: str, product_id: str | None = None) -> dict:
        matches = self.retrieve_relevant_documents(question, product_id)
        if not matches:
            return {
                "answer": "I could not find any relevant local product documentation for that question. Ask about battery life, RAM, warranty, or storage and I will answer from the local sample dataset when available.",
                "source_documents": [],
                "answer_confidence": "low",
            }
        best = matches[0]["content"]
        answer = best[:400]
        return {
            "answer": answer,
            "source_documents": [item["source"] for item in matches],
            "answer_confidence": "medium",
        }
