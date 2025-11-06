# Temporis – Timetable API (FastAPI + SQLModel + CSP)

## Run
```bash
pip install -r requirements.txt
uvicorn temporis.backend.app:app --reload --port 8000
```
Then:
- POST http://localhost:8000/init/seed
- POST http://localhost:8000/solve
- GET  http://localhost:8000/meta
- GET  http://localhost:8000/meta/timetable?view=class&id=1
```
DB: sqlite (timetable.db)
```

