from __future__ import annotations

from app.services.rag_service import RAGService


def main() -> None:
    rag = RAGService()
    docs = rag.ingest_documents()
    print(f"Indexed {len(docs)} FAQ/document chunks.")


if __name__ == "__main__":
    main()
