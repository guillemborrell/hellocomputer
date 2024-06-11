import os
from pathlib import Path

from typing_extensions import Self
from .db import DDB


class AnalyticsDB(DDB):
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
