from enum import StrEnum
from sqlalchemy import create_engine, text
from pathlib import Path


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
        self.engine = create_engine(
            "duckdb:///:memory:",
            connect_args={
                "preload_extensions": ["https", "spatial"],
                "config": {"memory_limit": "300mb"},
            },
        )
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
                with self.engine.connect() as conn:
                    conn.execute(
                        text(
                            f"""
                    CREATE SECRET (
                    TYPE GCS,
                    KEY_ID '{gcs_access}',
                    SECRET '{gcs_secret}')
                    """
                        )
                    )

                self.path_prefix = f"gcs://{bucket}"
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

    @property
    def db(self):
        return self.engine.raw_connection()
