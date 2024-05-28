from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from ..security import oauth2_scheme

# Scheme for the Authorization header

router = APIRouter()


@router.get("/new_session")
async def get_new_session(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    return str(uuid4())


@router.get("/greetings", response_class=PlainTextResponse)
async def get_greeting() -> str:
    return (
        "Hi! I'm a helpful assistant. Please upload or select a file "
        "and I'll try to analyze it following your orders"
    )
