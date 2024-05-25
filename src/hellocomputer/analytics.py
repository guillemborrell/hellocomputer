import duckdb
import os
from typing_extensions import Self


class DDB:
    def __init__(self):
        self.db = duckdb.connect()
        self.db.install_extension("spatial")
        self.db.install_extension("httpfs")
        self.db.load_extension("spatial")
        self.db.load_extension("httpfs")
        self.sheets = tuple()
        self.path = ""

    def gcs_secret(self, gcs_access: str, gcs_secret: str) -> Self:
        self.db.sql(f"""
            CREATE SECRET (
               TYPE GCS,
               KEY_ID '{gcs_access}',
               SECRET '{gcs_secret}')
               """)

        return self

    def load_metadata(self, path: str = "") -> Self:
        """For some reason, the header is not loaded"""
        self.db.sql(f"""
            create table metadata as (
            select
                *
            from
                st_read('{path}', 
                        layer='metadata'
                        )
            )""")
        self.sheets = tuple(
            self.db.query("select Field2 from metadata where Field1 = 'Sheets'")
            .fetchall()[0][0]
            .split(";")
        )
        self.path = path

        return self

    def dump_local(self, path) -> Self:
        # TODO: Port to fsspec and have a single dump file
        self.db.query(f"copy metadata to '{path}/metadata.csv'")

        for sheet in self.sheets:
            self.db.query(f"""
            copy 
                (
                select
                    *
                from
                    st_read
                        (
                        '{self.path}',
                        layer = '{sheet}'
                        )
                )
            to '{path}/{sheet}.csv'
                          """)
        return self

    def dump_gcs(self, bucketname, sid) -> Self:
        self.db.sql(f"copy metadata to 'gcs://{bucketname}/{sid}/metadata.csv'")

        for sheet in self.sheets:
            self.db.query(f"""
            copy 
                (
                select
                    *
                from
                    st_read
                        (
                        '{self.path}',
                        layer = '{sheet}'
                        )
                )
            to 'gcs://{bucketname}/{sid}/{sheet}.csv'
                          """)

        return self

    def load_folder_local(self, path: str) -> Self:
        self.sheets = tuple(
            self.query(
                f"select Field2 from read_csv_auto('{path}/metadata.csv') where Field1 = 'Sheets'"
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
                read_csv_auto('{path}/{sheet}.csv')
            )
            """)

        return self

    def load_folder_gcs(self, bucketname: str, sid: str) -> Self:
        self.sheets = tuple(
            self.query(
                f"select Field2 from read_csv_auto('gcs://{bucketname}/{sid}/metadata.csv') where Field1 = 'Sheets'"
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
                read_csv_auto('gcs://{bucketname}/{sid}/{sheet}.csv')
            )
            """)

        return self

    def load_description_local(self, path: str) -> Self:
        return self.query(
            f"select Field2 from read_csv_auto('{path}/metadata.csv') where Field1 = 'Description'"
        ).fetchall()[0][0]

    def load_description_gcs(self, bucketname: str, sid: str) -> Self:
        return self.query(
            f"select Field2 from read_csv_auto('gcs://{bucketname}/{sid}/metadata.csv') where Field1 = 'Description'"
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
        )

    def db_schema(self):
        return os.linesep.join(
            [
                "The schema of the database is the following:",
            ]
            + [self.table_schema(sheet) for sheet in self.sheets]
        )

    def query(self, sql, *args, **kwargs):
        return self.db.query(sql, *args, **kwargs)
