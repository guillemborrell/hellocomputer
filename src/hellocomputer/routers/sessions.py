from typing import List
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from starlette.requests import Request

from hellocomputer.db import StorageEngines
from hellocomputer.db.users import OwnershipDB

from ..config import settings

# Scheme for the Authorization header

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


@router.get("/sessions")
async def get_sessions(request: Request) -> List[str]:
    user_email = request.session.get("user").get("email")
    ownership = OwnershipDB(
        StorageEngines.gcs,
        gcs_access=settings.gcs_access,
        gcs_secret=settings.gcs_secret,
        bucket=settings.gcs_bucketname,
    )
    return ownership.sessions(user_email)
