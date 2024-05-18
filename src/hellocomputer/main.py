from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
import hellocomputer
from pathlib import Path
from pydantic import BaseModel
from langchain_community.chat_models import ChatAnyscale
from langchain_core.messages import HumanMessage, SystemMessage
from .config import settings

static_path = Path(hellocomputer.__file__).parent / "static"

app = FastAPI()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


@app.get("/greetings", response_class=PlainTextResponse)
async def get_greeting() -> str:
    model = "meta-llama/Meta-Llama-3-8B-Instruct"
    chat = ChatAnyscale(
        model_name=model,
        temperature=0.5,
        anyscale_api_key=settings.anyscale_api_key,
    )

    messages = [
        SystemMessage(content="You are a helpful AI that shares everything you know."),
        HumanMessage(
            content="Make a short presentation of yourself "
            "as an assistant in Spanish in about 20 words. "
            "You're capable of analyzing a file that a user "
            "has previously uploaded."
        ),
    ]

    model_response = await chat.ainvoke(messages)
    print(model_response.response_metadata)
    return model_response.content


app.mount(
    "/",
    StaticFiles(directory=static_path, html=True, packages=["bootstrap4"]),
    name="static",
)
