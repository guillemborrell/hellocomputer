import json
import os
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

import duckdb
import polars as pl

from hellocomputer.db import DDB
from hellocomputer.config import Settings, StorageEngines


class UserDB(DDB):
    def __init__(
        self,
        settings: Settings,
    ):
        super().__init__(settings)

        if settings.storage_engine == StorageEngines.gcs:
            self.path_prefix = f"gs://{settings.gcs_bucketname}/users"

        elif settings.storage_engine == StorageEngines.local:
            self.path_prefix = settings.path / "users"

        self.storage_engine = settings.storage_engine

    def dump_user_record(self, user_data: dict, record_id: UUID | None = None):
        df = pl.from_dict(user_data)  # noqa
        record_id = uuid4() if record_id is None else record_id
        query = f"COPY df TO '{self.path_prefix}/{record_id}.ndjson' (FORMAT JSON)"

        try:
            self.db.sql(query)
        except duckdb.duckdb.IOException as e:
            if self.storage_engine == StorageEngines.local:
                os.makedirs(self.path_prefix)
                self.db.sql(query)
            else:
                raise e

        return user_data

    def user_exists(self, email: str) -> bool:
        query = f"SELECT * FROM '{self.path_prefix}/*.ndjson' WHERE email = '{email}'"
        return self.db.sql(query).pl().shape[0] > 0

    @staticmethod
    def email(record: str) -> str:
        return json.loads(record)["email"]


class OwnershipDB(DDB):
    def __init__(
        self,
        settings: Settings,
    ):
        super().__init__(settings)

        if settings.storage_engine == StorageEngines.gcs:
            self.path_prefix = f"gs://{settings.gcs_bucketname}/owners"

        elif settings.storage_engine == StorageEngines.local:
            self.path_prefix = settings.path / "owners"

    def set_ownersip(self, user_email: str, sid: str, record_id: UUID | None = None):
        now = datetime.now().isoformat()
        record_id = uuid4() if record_id is None else record_id
        query = f"""
        COPY
          (
            SELECT
              '{user_email}' as email,
              '{sid}' as sid,
              '{now}' as timestamp
          )
        TO '{self.path_prefix}/{record_id}.csv'"""

        try:
            self.db.sql(query)
        except duckdb.duckdb.IOException:
            os.makedirs(self.path_prefix)
            self.db.sql(query)

        return sid

    def sessions(self, user_email: str) -> List[str]:
        try:
            return (
                self.db.sql(f"""
            SELECT
                sid
            FROM
                '{self.path_prefix}/*.csv'
            WHERE
                email = '{user_email}'
            ORDER BY
                timestamp ASC
            LIMIT 10
        """)
                .pl()
                .to_series()
                .to_list()
            )
        # If the table does not exist
        except duckdb.duckdb.IOException:
            return []
