from fastapi import FastAPI

from app.database.session import engine

app = FastAPI(
    title="Society Maintenance Tracker API",
    description="API for managing society maintenance complaints.",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    return {"status": "ok", "database": "connected"}