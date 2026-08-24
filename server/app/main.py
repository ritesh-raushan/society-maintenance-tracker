from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.categories import admin_router as categories_admin_router, public_router as categories_public_router
from app.complaints import admin_router as complaints_admin_router, public_router as complaints_public_router
from app.core.config import settings
from app.notices import admin_router as notices_admin_router, public_router as notices_public_router
from app.users import router as users_admin_router
from app.core.errors import AppError, app_error_handler
from app.database.session import engine

app = FastAPI(
    title="Society Maintenance Tracker API",
    description="API for managing society maintenance complaints.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)


@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    details = {
        ".".join(str(loc) for loc in error["loc"][1:]): error["msg"]
        for error in exc.errors()
    }

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": details,
            }
        },
    )


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(categories_public_router)
api_router.include_router(categories_admin_router)
api_router.include_router(complaints_public_router)
api_router.include_router(complaints_admin_router)
api_router.include_router(users_admin_router)
api_router.include_router(notices_public_router)
api_router.include_router(notices_admin_router)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    return {"status": "ok", "database": "connected"}
