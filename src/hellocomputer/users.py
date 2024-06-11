import json
import os
from pathlib import Path
from uuid import UUID, uuid4

import duckdb
import polars as pl

from .db import DDB, StorageEngines


class UserDB(DDB):
    def __init__(
        self,
        storage_engine: StorageEngines,
        path: Path | None = None,
        gcs_access: str | None = None,
        gcs_secret: str | None = None,
        bucket: str | None = None,
        **kwargs,
    ):
        super().__init__(storage_engine, path, gcs_access, gcs_secret, bucket, **kwargs)

        if storage_engine == StorageEngines.gcs:
            self.path_prefix = "gcs://{bucket}/users"

        elif storage_engine == StorageEngines.local:
            self.path_prefix = path / "users"

    def dump_user_record(self, user_data: dict, record_id: UUID | None = None):
        df = pl.from_dict(user_data)  # noqa
        record_id = uuid4() if record_id is None else record_id
        query = f"COPY df TO '{self.path_prefix}/{record_id}.ndjson' (FORMAT JSON)"

        try:
            self.db.sql(query)
        except duckdb.duckdb.IOException:
            os.makedirs(self.path_prefix)
            self.db.sql(query)

        return user_data

    def user_exists(self, email: str) -> bool:
        query = f"SELECT * FROM '{self.path_prefix}/*.ndjson' WHERE email = '{email}'"
        return self.db.sql(query).pl().shape[0] > 0

    @staticmethod
    def email(record: str) -> str:
        return json.loads(record)["email"]
