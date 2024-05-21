from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ..config import settings
from ..models import Chat

router = APIRouter()


@router.get("/query", response_class=PlainTextResponse, tags=["queries"])
async def query(sid: str = "") -> str:
    model = Chat(api_key=settings.anyscale_api_key).eval(
        system="You're an expert analyst", human="Do some analysis"
    )
    return model.last_response_content()
