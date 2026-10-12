from __future__ import annotations

from app.services.rag_service import RAGService


def answer_faq(question: str, product_id: str | None = None) -> dict:
    rag = RAGService()
    return rag.answer_question(question, product_id=product_id)
