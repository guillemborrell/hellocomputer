import os
from enum import StrEnum
from pathlib import Path

import duckdb
from typing_extensions import Self


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

    def load_xls(self, xls_path: Path) -> Self:
        """For some reason, the header is not loaded"""
        self.db.sql(f"""
            create table metadata as (
            select
                *
            from
                st_read('{xls_path}', 
                        layer='metadata'
                        )
            )""")
        self.sheets = tuple(
            self.db.query("select Field2 from metadata where Field1 = 'Sheets'")
            .fetchall()[0][0]
            .split(";")
        )

        for sheet in self.sheets:
            self.db.query(f"""
            create table {sheet} as  
                (
                select
                    *
                from
                    st_read
                        (
                        '{xls_path}',
                        layer = '{sheet}'
                        )
                )
                          """)

        self.loaded = True

        return self

    def dump(self) -> Self:
        # TODO: Create a decorator
        if not self.loaded:
            raise ValueError("Data should be loaded first")

        self.db.query(f"copy metadata to '{self.path_prefix}/metadata.csv'")

        for sheet in self.sheets:
            self.db.query(f"copy {sheet} to '{self.path_prefix}/{sheet}.csv'")
        return self

    def load_folder(self) -> Self:
        self.query(
            f"""
                create table metadata as (
                select
                    *
                from
                    read_csv_auto('{self.path_prefix}/metadata.csv')
                )
                """
        )
        self.sheets = tuple(
            self.query(
                """
                select
                    Field2
                from
                    metadata
                where
                    Field1 = 'Sheets'
                """
            )
            .fetchall()[0][0]
            .split(";")
        )

        # Load all the tables into the database
        for sheet in self.sheets:
            self.db.query(f"""
            create table {sheet} as (
            select
                *
            from
                read_csv_auto('{self.path_prefix}/{sheet}.csv')
            )
            """)

        self.loaded = True

        return self

    def load_description(self) -> Self:
        return self.query(
            """
            select
                Field2
            from
                metadata
            where
                Field1 = 'Description'"""
        ).fetchall()[0][0]

    @staticmethod
    def process_schema_row(row):
        return f"Column name: {row[0]}, Column type: {row[1]}"

    def table_schema(self, table: str):
        return os.linesep.join(
            [f"Table name: {table}"]
            + list(
                self.process_schema_row(r)
                for r in self.query(
                    f"select column_name, column_type from (describe {table})"
                ).fetchall()
            )
            + [os.linesep]
        )

    @property
    def schema(self):
        return os.linesep.join(
            [
                "The schema of the database is the following:",
            ]
            + [self.table_schema(sheet) for sheet in self.sheets]
        )

    def query(self, sql, *args, **kwargs):
        return self.db.query(sql, *args, **kwargs)

    def query_prompt(self, user_prompt: str) -> str:
        query = (
            f"The following sentence is the description of a query that "
            f"needs to be executed in a database: {user_prompt}"
        )

        return os.linesep.join(
            [
                query,
                self.schema,
                self.load_description(),
                "Return just the SQL statement",
            ]
        )
