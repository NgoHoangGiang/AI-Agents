# Architecture - Personal BA/DA/QC Copilot MVP

## 1. Objective
Build an internal AI Copilot MVP that can:
- ingest internal documents
- chunk and prepare text for retrieval
- answer future questions based on indexed knowledge
- support technical explanation for SQL/dbt content

## 2. In Scope
- FastAPI backend
- upload and ingest text-based documents
- chunking utility
- local raw file storage
- JSON response for chunk validation
- API documentation via Swagger

## 3. Out of Scope
- vector database
- embeddings
- semantic retrieval
- chat endpoint with LLM
- authentication
- long-term memory
- multi-agent workflow

## 4. Initial Components
- `main.py`: application entrypoint
- `routes/health.py`: health check endpoint
- `routes/documents.py`: document ingest endpoint
- `services/ingest_service.py`: file validation, reading, saving, chunking
- `utils/chunking.py`: chunk splitting logic
- `schemas/documents.py`: response models

## 5. Initial Flow
1. User uploads a `.md`, `.txt`, or `.sql` file
2. API validates file type and size
3. API reads UTF-8 text content
4. API saves raw file into `data/raw/`
5. API chunks content into overlapping segments
6. API returns chunk metadata and content in JSON

## 6. Next Steps
- add embeddings
- add vector store
- add retrieval endpoint
- add chat endpoint
- add citations