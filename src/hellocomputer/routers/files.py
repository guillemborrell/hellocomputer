import aiofiles
import duckdb
import polars as pl
import s3fs
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from ..config import settings

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

        db = duckdb.connect()
        db.install_extension("spatial")
        db.install_extension("httpfs")
        db.load_extension("httpfs")
        db.load_extension("spatial")

        db.sql(f"""
            CREATE SECRET (
               TYPE GCS,
               KEY_ID '{settings.gcs_access}',
               SECRET '{settings.gcs_secret}')
               """)

        db.sql(f"""
            create table metadata as (
            select
                *
            from
                st_read('{f.name}', 
                        layer='metadata',
                        open_options=['HEADERS_FORCE', 'FIELD_TYPES=auto']
                        )
            )""")

        metadata = db.query("select * from metadata").pl()
        sheets = metadata.select(pl.col("Key") == "Sheets")
        print(sheets)

        for sheet in sheets.to_dict():
            print(sheet)

        db.sql(
            f"""
            create table data as (
            select
                *
            from
                st_read('{f.name}', 
                        layer='data',
                        open_options=['HEADERS_FORCE', 'FIELD_TYPES=auto']
                        )
            )"""
        )

        db.sql(f"""
            copy
                data
            to
                'gcs://{settings.gcs_bucketname}/{sid}/data.csv';
            """)

        return JSONResponse(
            content={"message": "File uploaded successfully"}, status_code=200
        )
