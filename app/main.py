from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time

from app.config import settings
from app.database import create_tables
from app.logging_config import setup_logging, get_logger
from app.api.v1.api import api_router
from app.exceptions import BaseAppException, create_http_exception_from_app_exception

setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting up Saber Task API...")
    create_tables()
    logger.info("Database tables created/verified")
    yield
    logger.info("Shutting down Saber Task API...")


app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    logger.error(f"Application error: {exc.message}", extra={"details": exc.details})
    http_exc = create_http_exception_from_app_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "details": {}
        }
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} - {process_time:.4f}s",
        extra={"duration": process_time, "status_code": response.status_code}
    )

    return response


app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information."""
    return {
        "name": settings.title,
        "version": settings.version,
        "status": "running",
        "docs_url": "/docs" if settings.debug else "disabled",
        "api_prefix": settings.api_v1_str
    }
