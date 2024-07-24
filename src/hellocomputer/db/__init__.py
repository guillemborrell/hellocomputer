from hellocomputer.config import Settings, StorageEngines
from sqlalchemy import create_engine


class DDB:
    def __init__(
        self,
        settings: Settings,
    ):
        self.storage_engine = settings.storage_engine
        self.engine = create_engine("duckdb:///:memory:")
        self.db = self.engine.raw_connection()

        if self.storage_engine == StorageEngines.gcs:
            self.db.sql(f"""
                    CREATE SECRET (
                    TYPE GCS,
                    KEY_ID '{settings.gcs_access}',
                    SECRET '{settings.gcs_secret}')
                    """)

            self.path_prefix = f"gs://{settings.gcs_bucketname}"

        elif settings.storage_engine == StorageEngines.local:
            self.path_prefix = settings.path

    def query(self, sql, *args, **kwargs):
        return self.db.query(sql, *args, **kwargs)
