from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from hellocomputer.db import StorageEngines
from hellocomputer.db.sessions import SessionDB
from hellocomputer.extraction import extract_code_block

from ..config import settings
from ..models import Chat

router = APIRouter()


@router.get("/query", response_class=PlainTextResponse, tags=["queries"])
async def query(sid: str = "", q: str = "") -> str:
    llm = Chat(api_key=settings.anyscale_api_key, temperature=0.5)
    db = SessionDB(
        StorageEngines.gcs,
        gcs_access=settings.gcs_access,
        gcs_secret=settings.gcs_secret,
        bucket=settings.gcs_bucketname,
        sid=sid,
    ).load_folder()

    chat = await llm.eval("You're a DUCKDB expert", db.query_prompt(q))
    query = extract_code_block(chat.last_response_content())
    result = str(db.query(query))

    return result
