from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from hellocomputer.analytics import DDB, StorageEngines
from hellocomputer.extraction import extract_code_block

from ..config import settings
from ..models import Chat

router = APIRouter()


@router.get("/query", response_class=PlainTextResponse, tags=["queries"])
async def query(sid: str = "", q: str = "") -> str:
    chat = Chat(api_key=settings.anyscale_api_key, temperature=0.5)
    db = DDB(
        StorageEngines.gcs,
        gcs_access=settings.gcs_access,
        gcs_secret=settings.gcs_secret,
        bucket=settings.gcs_bucketname,
        sid=sid,
    ).load_folder()

    chat = await chat.eval("You're an expert sql developer", db.query_prompt(q))
    query = extract_code_block(chat.last_response_content())
    result = str(db.query(query))
    print(result)

    return result
