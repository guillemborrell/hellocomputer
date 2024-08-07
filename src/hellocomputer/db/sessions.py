import os
from pathlib import Path

import duckdb
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from typing_extensions import Self

from hellocomputer.config import Settings, settings, StorageEngines
from hellocomputer.models import AvailableModels

from . import DDB


class SessionDB(DDB):
    def set_session(self, sid):
        self.sid = sid
        # Override storage engine for sessions
        if settings.storage_engine == StorageEngines.gcs:
            self.path_prefix = f"gs://{settings.gcs_bucketname}/sessions/{sid}"
        elif settings.storage_engine == StorageEngines.local:
            self.path_prefix = settings.path / "sessions" / sid

    def load_xls(self, xls_path: Path) -> Self:
        """For some reason, the header is not loaded"""
        self.db.sql("load spatial")
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

        try:
            self.db.query(f"copy metadata to '{self.path_prefix}/metadata.csv'")
        except duckdb.duckdb.IOException as e:
            # Create the folder
            if self.storage_engine == StorageEngines.local:
                os.makedirs(self.path_prefix)
                self.db.query(f"copy metadata to '{self.path_prefix}/metadata.csv'")
            else:
                raise e

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
    def schema(self) -> str:
        return os.linesep.join(
            [
                "The schema of the database is the following:",
            ]
            + [self.table_schema(sheet) for sheet in self.sheets]
        )

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

    @property
    def llmsql(self):
        return SQLDatabase(self.engine, ignore_tables=["metadata"])

    @property
    def sql_toolkit(self) -> SQLDatabaseToolkit:
        llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=AvailableModels.llama_medium,
            temperature=0.3,
        )
        return SQLDatabaseToolkit(db=self.llmsql, llm=llm)
