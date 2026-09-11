import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import check_database_connection
from app.routes.api import router as api_router

app = FastAPI(
    title="UdyamSaathi API",
    description="Core APIs for the UdyamSaathi prototype.",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Welcome to UdyamSaathi API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "udyamsaathi-api"}


@app.get("/health/db")
def database_health_check() -> dict[str, str]:
    try:
        if check_database_connection():
            return {"database": "connected"}
    except (RuntimeError, psycopg.Error):
        pass
    return {"database": "unavailable"}
