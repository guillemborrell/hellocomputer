import duckdb
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
        self.db.sql(f"copy metadata to 'gcs://{bucketname}/{sid}/data.csv'")

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
        return self

    def load_folder_gcs(self, path: str) -> Self:
        return self

    def query(self, sql, *args, **kwargs):
        return self.db.query(sql, *args, **kwargs)
