from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from langchain_core.messages import HumanMessage
from starlette.requests import Request

from hellocomputer.graph import app

router = APIRouter()


@router.get("/query", response_class=PlainTextResponse, tags=["queries"])
async def query(request: Request, sid: str = "", q: str = "") -> str:
    user = request.session.get("user")  # noqa
    response = await app.ainvoke({"messages": [HumanMessage(content=q)]})
    return response["messages"][-1].content
