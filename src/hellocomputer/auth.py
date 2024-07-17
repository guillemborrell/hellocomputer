from starlette.requests import Request

from .config import settings


def get_user(request: Request) -> dict:
    """_summary_

    Args:
        request (Request): _description_

    Returns:
        dict: _description_
    """
    if settings.auth:
        return request.session.get("user")
    else:
        return {"email": "test@test.com"}


def get_user_email(request: Request) -> str:
    """_summary_

    Args:
        request (Request): _description_

    Returns:
        str: _description_
    """
    if settings.auth:
        return request.session.get("user").get("email")
    else:
        return "test@test.com"
