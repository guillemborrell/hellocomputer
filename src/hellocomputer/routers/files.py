import aiofiles

# import s3fs
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from starlette.requests import Request

from ..config import settings
from ..db import StorageEngines
from ..sessions import SessionDB
from ..users import OwnershipDB

router = APIRouter()


# Configure the S3FS with your Google Cloud Storage credentials
# gcs = s3fs.S3FileSystem(
#     key=settings.gcs_access,
#     secret=settings.gcs_secret,
#     client_kwargs={"endpoint_url": "https://storage.googleapis.com"},
# )
# bucket_name = settings.gcs_bucketname


@router.post("/upload", tags=["files"])
async def upload_file(request: Request, file: UploadFile = File(...), sid: str = ""):
    async with aiofiles.tempfile.NamedTemporaryFile("wb") as f:
        content = await file.read()
        await f.write(content)
        await f.flush()

        (
            SessionDB(
                StorageEngines.gcs,
                gcs_access=settings.gcs_access,
                gcs_secret=settings.gcs_secret,
                bucket=settings.gcs_bucketname,
                sid=sid,
            )
            .load_xls(f.name)
            .dump()
        )

        OwnershipDB(
            StorageEngines.gcs,
            gcs_access=settings.gcs_access,
            gcs_secret=settings.gcs_secret,
            bucket=settings.gcs_bucketname,
        ).set_ownersip(request.session.get("user").get("email"), sid)

        return JSONResponse(
            content={"message": "File uploaded successfully"}, status_code=200
        )
