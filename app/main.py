from contextlib import asynccontextmanager
import os

from anyio import to_thread
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, ORJSONResponse
from sqlalchemy.orm import Session

from app.common.dependencies import get_session
from app.common.exceptions import CustomHTTPException, NotFound
from app.core.handlers import (
    base_exception_handler,
    custom_http_exception_handler,
    request_validation_exception_handler,
)
from app.poi.apis import router as poi_router
from app.user.apis import router as user_router


# Lifespan (startup, shutdown)
@asynccontextmanager
async def lifespan(_: FastAPI):
    """This is the startup and shutdown code for the FastAPI application."""
    # Startup code
    print("Starting Server...")

    # Bigger Threadpool i.e you send a bunch of requests it will handle a max of 1000 at a time, the default is 40 # pylint: disable=line-too-long
    limiter = to_thread.current_default_thread_limiter()
    limiter.total_tokens = 1000

    # Shutdown Code
    yield
    print("Shutting Down Server...")


app = FastAPI(
    title="Behemoth FastAPI",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    docs_url="/",
    contact={
        "name": "GrandGale Technologies",
        "url": "https://github.com/GrandGaleTechnologies",
        "email": "angobello0@gmail.com",
    },
)

# Allowed Origins
origins = ["*"]

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    GZipMiddleware,
    minimum_size=5000,  # Minimum size of the response before it is compressed in bytes
)


# Exception Handlers
app.add_exception_handler(Exception, base_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore
app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)  # type: ignore


# Healthcheck
@app.get("/health", include_in_schema=False)
async def health(_: Session = Depends(get_session)):
    """App Healthcheck"""
    return {"status": "Ok!"}


# Media download
@app.get("/media")
async def media_download(
    path: str,
):
    """
    Download media
    """
    if not os.path.exists(f"media/{path}") or not os.path.isfile(f"media/{path}"):
        raise NotFound("File not found")

    return FileResponse(path=f"media/{path}")


# Routers
app.include_router(user_router, prefix="/user", tags=["User APIs"])
app.include_router(poi_router, prefix="/poi", tags=["POI APIs"])
