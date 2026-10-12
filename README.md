# Agentic Shopping Assistant

This project is a sample agentic commerce application for laptop recommendations. It combines a local SQLite catalog, deterministic scoring logic, optional OpenAI-powered explanations, and a FAQ retrieval layer built around ChromaDB-like local documents.

## Features

- Natural-language requirement extraction for shopping requests
- Local product catalog filtering and comparison
- Budget and inventory validation using SQLite as the source of truth
- Transparent ranking logic with score breakdowns
- Optional LLM explanations when an API key is configured
- FAQ retrieval grounded in local docs
- FastAPI backend with Swagger UI
- Streamlit frontend

## Project structure

- `app/` — FastAPI app, graph workflow, services, and agent nodes
- `data/` — local CSV product catalog and FAQ documents
- `scripts/` — database seeding and document ingestion scripts
- `frontend/` — Streamlit UI
- `tests/` — automated pytest suite

## Setup on Windows

From PowerShell:

```powershell
cd "C:\Users\bandi\Desktop\Ecommerce1\agentic-shopping-assistant"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `.env` with your real values if needed. The app works for catalog search, pricing, and tests without an OpenAI key. A missing key only disables AI-generated explanations.

## Initialize the sample database

```powershell
python -m scripts.seed_database
```

## Ingest FAQ documents

```powershell
python -m scripts.ingest_documents
```

## Run the backend

```powershell
uvicorn app.main:app --reload --port 8765
```

Open Swagger UI at `http://127.0.0.1:8765/docs`.

## Run the frontend

In a second terminal:

```powershell
cd "C:\Users\bandi\Desktop\Ecommerce1\agentic-shopping-assistant"
.\.venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```

## Deploy

The repository includes a Render Blueprint for both the FastAPI backend and Streamlit UI and pins the deployment runtime to Python 3.12. In Render, create or sync the Blueprint from this GitHub repository. The backend health check uses `/health`; the UI is configured to call the backend automatically.

The deployed services are available at `https://ecommerce-agent-api.onrender.com` and `https://ecommerce-agent-ui.onrender.com`. Free instances spin down after inactivity, so the first request may take 50 seconds or more.

The free backend uses the included sample catalog and SQLite database. Data written to SQLite is not guaranteed to persist across service restarts.

## Example API calls

### Product search

```bash
curl "http://127.0.0.1:8000/products/search?category=laptop&budget=60000&min_ram=16"
```

### Shopping request

```bash
curl -X POST "http://127.0.0.1:8000/assistant/chat" \
  -H "Content-Type: application/json" \
  -d '{"request_text":"I need a laptop under ₹60,000 for Python programming, machine learning basics, and online classes. I prefer 16 GB RAM and good battery life."}'
```

### FAQ request

```bash
curl -X POST "http://127.0.0.1:8000/assistant/faq" \
  -H "Content-Type: application/json" \
  -d '{"question":"Which laptop is best for Python and online classes?"}'
```

### Cart preview

```bash
curl -X POST "http://127.0.0.1:8000/cart/preview" \
  -H "Content-Type: application/json" \
  -d '{"cart_id":"preview-cart","items":[{"product_id":"LAP-002","quantity":1}]}'
```

### Cart confirmation

```bash
curl -X POST "http://127.0.0.1:8000/cart/confirm" \
  -H "Content-Type: application/json" \
  -d '{"cart_id":"sample-cart","items":[{"product_id":"LAP-002","quantity":1}],"confirmed":true}'
```

## Testing

```powershell
pytest -q
```

## Notes

- Catalog pricing and inventory are sample data only.
- Do not use this project for live payment workflows.
- The cart system performs simulated confirmation checks server-side and never creates a real order.
- The RAG layer operates on local documents and does not claim to know anything not present in those docs.

## Troubleshooting

- If a dependency fails, recreate the venv and rerun `pip install -r requirements.txt`.
- If the FastAPI app cannot connect to the database, ensure `DATABASE_URL` points to a writable SQLite file.
- If OpenAI requests fail, the catalog and tests still work because the app gracefully falls back to local deterministic logic.
