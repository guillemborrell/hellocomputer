from uuid import uuid4

from fastapi import APIRouter
from starlette.requests import Request
from fastapi.responses import PlainTextResponse


# Scheme for the Authorization header

router = APIRouter()


@router.get("/new_session")
async def get_new_session(request: Request) -> str:
    user = request.session.get("user")
    print(user)
    return str(uuid4())


@router.get("/greetings", response_class=PlainTextResponse)
async def get_greeting() -> str:
    return (
        "Hi! I'm a helpful assistant. Please upload or select a file "
        "and I'll try to analyze it following your orders"
    )
