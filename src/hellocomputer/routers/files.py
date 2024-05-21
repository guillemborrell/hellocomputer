import aiofiles
import s3fs
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from ..config import settings
from ..analytics import DDB

router = APIRouter()


# Configure the S3FS with your Google Cloud Storage credentials
gcs = s3fs.S3FileSystem(
    key=settings.gcs_access,
    secret=settings.gcs_secret,
    client_kwargs={"endpoint_url": "https://storage.googleapis.com"},
)
bucket_name = settings.gcs_bucketname


@router.post("/upload", tags=["files"])
async def upload_file(file: UploadFile = File(...), sid: str = ""):
    async with aiofiles.tempfile.NamedTemporaryFile("wb") as f:
        content = await file.read()
        await f.write(content)
        await f.flush()

        gcs.makedir(f"{settings.gcs_bucketname}/{sid}")

        (
            DDB()
            .gcs_secret(settings.gcs_secret, settings.gcs_secret)
            .load_metadata(f.name)
            .load_data()
            .save_gcs(settings.gcs_bucketname, sid)
        )

        return JSONResponse(
            content={"message": "File uploaded successfully"}, status_code=200
        )
