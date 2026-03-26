# Runbook - Local Development

## 1. Go to API folder

```bash
cd apps/api
```

## 2. Create virtual environment

### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Git Bash / macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run API

```bash
uvicorn app.main:app --reload
```

## 5. Open API
- Root: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## 6. Test ingest endpoint
Use Swagger UI:
- Endpoint: `POST /documents/ingest`
- Upload one file: `.md`, `.txt`, or `.sql`

## 7. Expected result
API returns:
- file name
- file type
- saved path
- character count
- total chunks
- chunk list