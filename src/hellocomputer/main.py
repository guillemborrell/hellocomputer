from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import hellocomputer
from pathlib import Path

static_path = Path(hellocomputer.__file__).parent / "static"

app = FastAPI()

app.mount(
    "/",
    StaticFiles(directory=static_path, html=True, packages=["bootstrap4"]),
    name="static",
)
