# Personal BA/DA/QC Copilot - MVP

Repo này dùng để build AI Copilot cá nhân cho việc:
- hỏi đáp tài liệu nội bộ
- giải thích SQL/dbt
- draft checklist/testcase

## Current features

- Document ingest
- Document listing
- Keyword search
- Semantic search with local embeddings
- Grounded chat on indexed documents
- SQL explanation endpoint

## Current backend features

- Document ingest
- Document metadata listing
- Keyword search
- Semantic search with local embeddings
- Grounded chat on indexed documents
- SQL explanation
- Document summarization
- Draft checklist generation

## Run locally

```bash
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

## Bước 2.2 — `docs/runbook.md`
Đảm bảo có:
- cách tạo `.venv`
- cách install dependencies
- cách chạy server
- các endpoint hiện có

## Bước 2.3 — `docs/architecture.md`
Cập nhật feature hiện tại:
- documents module
- retrieval module
- grounded chat
- sql explain