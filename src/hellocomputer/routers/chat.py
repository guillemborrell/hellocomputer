from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from langchain_core.messages import HumanMessage
from starlette.requests import Request

from hellocomputer.graph import app

import os

router = APIRouter()


@router.get("/query", response_class=PlainTextResponse, tags=["chat"])
async def query(request: Request, sid: str = "", q: str = "") -> str:
    user = request.session.get("user")  # noqa
    content = f"{q}{os.linesep}******{sid}******"
    response = await app.ainvoke(
        {"messages": [HumanMessage(content=content)]},
    )
    return response["messages"][-1].content
