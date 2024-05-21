from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/new_session")
async def get_new_session() -> str:
    return str(uuid4())


@router.get("/greetings", response_class=PlainTextResponse)
async def get_greeting() -> str:
    return (
        "Hi! I'm a helpful assistant. Please upload or select a file "
        "and I'll try to analyze it following your orders"
    )
