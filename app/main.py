import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.auth import router as auth_router
from app.api.routers.files import router as files_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup", extra={"env": settings.app_env})
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.include_router(health_router)
    app.include_router(auth_router)
    # app.include_router(auth_router, prefix="/auth", tags=["auth"])
    # app.include_router(files_router, prefix="/files", tags=["files"])
    app.include_router(files_router)

    return app


app = create_app()
