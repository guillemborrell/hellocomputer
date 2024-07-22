from enum import StrEnum
from pathlib import Path

import duckdb
from sqlalchemy import create_engine


class StorageEngines(StrEnum):
    local = "Local"
    gcs = "GCS"


class DDB:
    def __init__(
        self,
        storage_engine: StorageEngines,
        path: Path | None = None,
        gcs_access: str | None = None,
        gcs_secret: str | None = None,
        bucket: str | None = None,
        **kwargs,
    ):
        self.db = duckdb.connect(":memory:")
        # Assume extension autoloading
        # self.db.sql("load httpfs")
        # self.db.sql("load spatial")
        self.storage_engine = storage_engine
        self.sheets = tuple()
        self.loaded = False

        if storage_engine == StorageEngines.gcs:
            if all(
                (
                    gcs_access is not None,
                    gcs_secret is not None,
                    bucket is not None,
                )
            ):
                self.db.sql(f"""
                    CREATE SECRET (
                    TYPE GCS,
                    KEY_ID '{gcs_access}',
                    SECRET '{gcs_secret}')
                    """)

                self.path_prefix = f"gs://{bucket}"
            else:
                raise ValueError(
                    "With GCS storage engine you need to provide "
                    "the gcs_access, gcs_secret, and bucket keyword arguments"
                )

        elif storage_engine == StorageEngines.local:
            if path is not None:
                self.path_prefix = path
            else:
                raise ValueError(
                    "With local storage you need to provide the path keyword argument"
                )
            

    def query(self, sql, *args, **kwargs):
        return self.db.query(sql, *args, **kwargs)

    @property
    def engine(self):
        return create_engine("duckdb:///:memory:")
