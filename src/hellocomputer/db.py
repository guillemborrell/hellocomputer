from enum import StrEnum
import duckdb
from pathlib import Path


class StorageEngines(StrEnum):
    local = "Local"
    gcs = "GCS"


class DDB:
    def __init__(
        self,
        storage_engine: StorageEngines,
        sid: str | None = None,
        path: Path | None = None,
        gcs_access: str | None = None,
        gcs_secret: str | None = None,
        bucket: str | None = None,
        **kwargs,
    ):
        self.db = duckdb.connect()
        self.db.install_extension("spatial")
        self.db.install_extension("httpfs")
        self.db.load_extension("spatial")
        self.db.load_extension("httpfs")
        self.sheets = tuple()
        self.loaded = False

        if storage_engine == StorageEngines.gcs:
            if all(
                (
                    gcs_access is not None,
                    gcs_secret is not None,
                    bucket is not None,
                    sid is not None,
                )
            ):
                self.db.sql(f"""
                    CREATE SECRET (
                    TYPE GCS,
                    KEY_ID '{gcs_access}',
                    SECRET '{gcs_secret}')
                    """)
                self.path_prefix = f"gcs://{bucket}/sessions/{sid}"
            else:
                raise ValueError(
                    "With GCS storage engine you need to provide "
                    "the gcs_access, gcs_secret, sid, and bucket keyword arguments"
                )

        elif storage_engine == StorageEngines.local:
            if path is not None:
                self.path_prefix = path
            else:
                raise ValueError(
                    "With local storage you need to provide the path keyword argument"
                )
