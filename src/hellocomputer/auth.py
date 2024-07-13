from starlette.requests import Request
from .config import settings


def get_user(request: Request) -> dict:
    if settings.auth:
        return request.session.get("user")
    else:
        return {"email": "test@test.com"}


def get_user_email(request: Request) -> str:
    if settings.auth:
        return request.session.get("user").get("email")
    else:
        return "test@test.com"
