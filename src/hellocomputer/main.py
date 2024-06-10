from pathlib import Path

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth, OAuthError
from pydantic import BaseModel
import json


import hellocomputer

from .routers import analysis, files, sessions
from .config import settings

static_path = Path(hellocomputer.__file__).parent / "static"

oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.auth0_client_id,
    client_secret=settings.auth0_client_secret,
    client_kwargs={"scope": "openid profile email", "verify": False},
    server_metadata_url=f"https://{settings.auth0_domain}/.well-known/openid-configuration",
)
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)


@app.get("/")
async def homepage(request: Request):
    user = request.session.get("user")
    if user:
        print(json.dumps(user))
        return RedirectResponse("/app")

    with open(static_path / "login.html") as f:
        return HTMLResponse(f.read())


@app.route("/login")
async def login(request: Request):
    return await oauth.auth0.authorize_redirect(
        request,
        redirect_uri=f"{settings.base_url}/callback",
    )


@app.route("/callback", methods=["GET", "POST"])
async def callback(request: Request):
    try:
        token = await oauth.auth0.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"<h1>{error.error}</h1>")
    user = token.get("userinfo")
    if user:
        request.session["user"] = dict(user)

    return RedirectResponse(url="/app")


@app.route("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@app.route("/user")
async def user(request: Request):
    user = request.session.get("user")
    return user


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
    "/app",
    StaticFiles(directory=static_path, html=True),
    name="static",
)
