from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

from hellocomputer.config import StorageEngines, settings
from hellocomputer.db.users import UserDB

router = APIRouter()

oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.auth0_client_id,
    client_secret=settings.auth0_client_secret,
    client_kwargs={"scope": "openid profile email", "verify": False},
    server_metadata_url=f"https://{settings.auth0_domain}/.well-known/openid-configuration",
)


@router.get("/login")
async def login(request: Request):
    return await oauth.auth0.authorize_redirect(
        request,
        redirect_uri=f"{settings.base_url}/callback",
    )


@router.route("/callback", methods=["GET", "POST"])
async def callback(request: Request):
    try:
        token = await oauth.auth0.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"<h1>{error.error}</h1>")
    user = token.get("userinfo")
    if user:
        user_info = dict(user)
        request.session["user"] = user_info
        user_db = UserDB(
            StorageEngines.gcs,
            gcs_access=settings.gcs_access,
            gcs_secret=settings.gcs_secret,
            bucket=settings.gcs_bucketname,
        )
        user_db.dump_user_record(user_info)

    return RedirectResponse(url="/app")


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@router.get("/user")
async def user(request: Request):
    user = request.session.get("user")
    return user
