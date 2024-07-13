from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

import hellocomputer

from .auth import get_user
from .config import settings
from .routers import analysis, auth, files, health, sessions

static_path = Path(hellocomputer.__file__).parent / "static"

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)


@app.get("/")
async def homepage(request: Request):
    user = get_user(request)
    if user:
        return RedirectResponse("/app")

    with open(static_path / "login.html") as f:
        return HTMLResponse(f.read())


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(static_path / "img" / "favicon.ico")


app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(files.router)
app.include_router(analysis.router)
app.include_router(auth.router)
app.mount(
    "/app",
    StaticFiles(directory=static_path, html=True),
    name="static",
)
