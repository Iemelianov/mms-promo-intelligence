"""
FastAPI Application

Main FastAPI application setup and configuration.
"""

import os
import logging
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, ValidationError

from .routes import discovery, scenarios, optimization, creative, data, auth, postmortem, chat
from middleware.errors import (
    APIError,
    api_error_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from middleware.rate_limit import limiter, rate_limit_exceeded_handler
from db.base import Base
from db.session import engine

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Phoenix observability setup
try:
    from phoenix.otel import register
    phoenix_api_key = os.getenv("PHOENIX_API_KEY")
    if phoenix_api_key:
        register()
        logger.info("Phoenix observability enabled")
    else:
        logger.info("Phoenix API key not found, observability disabled")
except ImportError:
    logger.warning("Phoenix not installed, observability disabled")

app = FastAPI(
    title="Promo Scenario Co-Pilot API",
    description="AI-powered promotional campaign planning and optimization system",
    version="1.0.0",
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


class Settings(BaseModel):
    database_url: str
    jwt_secret_key: str
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"


def validate_settings():
    """Validate critical environment variables."""
    try:
        Settings(
            database_url=os.getenv("DATABASE_URL", ""),
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", ""),
            environment=os.getenv("ENVIRONMENT", "development"),
            cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000"),
        )
    except ValidationError as exc:
        logger.warning(f"Configuration validation warning: {exc}")


@app.on_event("startup")
async def startup_event():
    """Startup tasks."""
    validate_settings()
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured")
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Could not initialize database tables: {exc}")

# Request ID and logging middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Add request ID and log requests for observability."""
    import time
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    logger.info(
        f"Request [{request_id}]: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["API-Version"] = "v1"
        if os.getenv("API_DEPRECATED") == "true":
            response.headers["Deprecation"] = "true"
        
        logger.info(
            f"Response [{request_id}]: {response.status_code} - {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Error [{request_id}]: {str(e)} - {process_time:.3f}s",
            exc_info=True
        )
        raise

# API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["discovery"])
app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["scenarios"])
app.include_router(optimization.router, prefix="/api/v1/optimization", tags=["optimization"])
app.include_router(creative.router, prefix="/api/v1/creative", tags=["creative"])
app.include_router(data.router, prefix="/api/v1/data", tags=["data"])
app.include_router(postmortem.router, prefix="/api/v1/postmortem", tags=["postmortem"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Promo Scenario Co-Pilot API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

