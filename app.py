from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .routers import meta, seed, solve

app = FastAPI(title="Temporis Timetable API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(seed.router)
app.include_router(meta.router)
app.include_router(solve.router)

@app.get("/")
def root():
    return {"ok": True, "service": "temporis"}
