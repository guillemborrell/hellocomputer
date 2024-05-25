from pathlib import Path

from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import hellocomputer

from .routers import files, sessions, analysis

static_path = Path(hellocomputer.__file__).parent / "static"

app = FastAPI()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


app.include_router(sessions.router)
app.include_router(files.router)
app.include_router(analysis.router)
app.mount(
    "/",
    StaticFiles(directory=static_path, html=True, packages=["bootstrap4"]),
    name="static",
)
