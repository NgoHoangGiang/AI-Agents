# Backend E2E Test Checklist

## 1. Documents
- [ ] POST /documents/ingest with valid .md file
- [ ] GET /documents returns uploaded documents
- [ ] GET /documents/search returns keyword matches
- [ ] POST /documents/embeddings/rebuild completes successfully
- [ ] GET /documents/semantic-search returns semantic matches

## 2. Chat
- [ ] POST /chat answers using indexed document chunks
- [ ] POST /chat returns citations
- [ ] POST /chat returns used_chunks
- [ ] POST /chat handles unrelated question gracefully

## 3. SQL Explain
- [ ] POST /explain-sql handles simple aggregation query
- [ ] POST /explain-sql handles join query
- [ ] POST /explain-sql handles CTE query
- [ ] POST /explain-sql rejects empty input properly

## 4. Summarize
- [ ] POST /summarize-document with document_id
- [ ] POST /summarize-document with raw_text
- [ ] POST /summarize-document extracts open questions
- [ ] POST /summarize-document rejects invalid input properly

## 5. Draft Checklist
- [ ] POST /draft-checklist with document_id
- [ ] POST /draft-checklist with raw_text
- [ ] POST /draft-checklist handles booking rules case
- [ ] POST /draft-checklist rejects invalid input properly