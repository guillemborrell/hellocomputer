from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ..config import settings
from ..models import Chat

from hellocomputer.analytics import DDB
from hellocomputer.extraction import extract_code_block

import os

router = APIRouter()


@router.get("/query", response_class=PlainTextResponse, tags=["queries"])
async def query(sid: str = "", q: str = "") -> str:
    query = f"Write a query that {q} in the current database"

    chat = Chat(api_key=settings.anyscale_api_key, temperature=0.5)
    db = (
        DDB()
        .gcs_secret(settings.gcs_secret, settings.gcs_secret)
        .load_folder_gcs(settings.gcs_bucketname, sid)
    )

    prompt = os.linesep.join(
        [
            query,
            db.db_schema(),
            db.load_description_gcs(settings.gcs_bucketname, sid),
            "Return just the SQL statement",
        ]
    )

    chat = await chat.eval("You're an expert sql developer", prompt)
    query = extract_code_block(chat.last_response_content())

    return str(db.query(query))
