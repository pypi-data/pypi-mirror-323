import logging
import warnings
import pandas as pd
import numpy as np
import datetime
from trino.dbapi import connect
from trino.auth import BasicAuthentication
from trino.transaction import IsolationLevel
from ..y4a_credentials import get_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

warnings.filterwarnings("ignore")


class TrinoUtils:
    def __init__(
        self,
        account_name: str = 'sop_dev',
        trino_host: str = 'sop-trino.yes4all.internal',
        trino_account: str = '',
        trino_password: str = '',
    ) -> None:
        self.account_name = account_name
        self.trino_host = trino_host
        self.trino_account = trino_account
        self.trino_password = trino_password

    def connect(
        self,
        isolation_level=IsolationLevel.AUTOCOMMIT,
    ):
        credentials = get_credentials(
            platform='trino',
            account_name=self.account_name,
        )

        if self.trino_account:
            if not self.trino_password:
                raise Exception(
                    'password must not be empty when '
                    'providing specific account'
                )
            else:
                conn = connect(
                    host=self.trino_host,
                    port="8443",
                    user=self.trino_account,
                    auth=BasicAuthentication(
                        self.trino_account,
                        self.trino_password,
                    ),
                    catalog="",
                    http_scheme="https",
                    verify=False,
                    schema="",
                    isolation_level=isolation_level,
                )
        else:
            conn = connect(
                host=self.trino_host,
                port="8443",
                user=self.trino_account,
                auth=BasicAuthentication(
                    credentials['user_name'],
                    credentials['password'],
                ),
                catalog="",
                http_scheme="https",
                verify=False,
                schema="",
                isolation_level=isolation_level,
            )

        return conn

    def get_data(
        self,
        sql: str,
    ) -> pd.DataFrame:
        """
        Get data from the given SQL query

        :param sql: SQL query to get data

        :return: dataframe
        """

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            df = pd.DataFrame(
                rows,
                columns=[
                    desc[0] for desc in cur.description
                ],
            )
            cur.close()
            conn.close()
            return df
        except Exception:
            cur.close()
            conn.close()
            raise

    def execute(
        self,
        sql: str,
    ) -> list:
        """
        Execute the given SQL query

        :param sql: SQL query to execute

        :return: list of query output
        """

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql)
            output = cur.fetchall()
            cur.close()
            conn.close()
            return output
        except Exception:
            cur.close()
            conn.close()
            raise

    # Iceberg integration
    def iceberg_get_valid_dtype(self) -> list:
        """
        Get valid data type in iceberg table

        :return: list contains details information about data type
        """

        return [
            {
                "Type": "boolean",
                "Parquet physical type": "boolean",
                "Logical type": None,
                "Notes": None
            },
            {
                "Type": "int",
                "Parquet physical type": "int",
                "Logical type": None,
                "Notes": None
            },
            {
                "Type": "long",
                "Parquet physical type": "long",
                "Logical type": None,
                "Notes": None
            },
            {
                "Type": "float",
                "Parquet physical type": "float",
                "Logical type": None,
                "Notes": None
            },
            {
                "Type": "double",
                "Parquet physical type": "double",
                "Logical type": None,
                "Notes": None
            },
            {
                "Type": "decimal(P,S)",
                "Parquet physical type": "P <= 9: int32, P <= 18: "
                "int64, fixed otherwise",
                "Logical type": "DECIMAL(P,S)",
                "Notes": "Fixed must use the minimum number "
                "of bytes that can store P."
            },
            {
                "Type": "date",
                "Parquet physical type": "int32",
                "Logical type": "DATE",
                "Notes": "Stores days from 1970-01-01."
            },
            {
                "Type": "time",
                "Parquet physical type": "int64",
                "Logical type": "TIME_MICROS with adjustToUtc=false",
                "Notes": "Stores microseconds from midnight."
            },
            {
                "Type": "timestamp",
                "Parquet physical type": "int64",
                "Logical type": "TIMESTAMP_MICROS with adjustToUtc=false",
                "Notes": "Stores microseconds from 1970-01-01 00:00:00.000000."
            },
            {
                "Type": "timestamptz",
                "Parquet physical type": "int64",
                "Logical type": "TIMESTAMP_MICROS with adjustToUtc=true",
                "Notes": "Stores microseconds from 1970-01-01 "
                "00:00:00.000000 UTC."
            },
            {
                "Type": "timestamp_ns",
                "Parquet physical type": "int64",
                "Logical type": "TIMESTAMP_NANOS with adjustToUtc=false",
                "Notes": "Stores nanoseconds from "
                "1970-01-01 00:00:00.000000000."
            },
            {
                "Type": "timestamptz_ns",
                "Parquet physical type": "int64",
                "Logical type": "TIMESTAMP_NANOS with adjustToUtc=true",
                "Notes": "Stores nanoseconds from "
                "1970-01-01 00:00:00.000000000 UTC."
            },
            {
                "Type": "string",
                "Parquet physical type": "binary",
                "Logical type": "UTF8",
                "Notes": "Encoding must be UTF-8."
            },
            {
                "Type": "uuid",
                "Parquet physical type": "fixed_len_byte_array[16]",
                "Logical type": "UUID",
                "Notes": None
            },
            {
                "Type": "fixed(L)",
                "Parquet physical type": "fixed_len_byte_array[L]",
                "Logical type": None,
                "Notes": None
            },
            {
                "Type": "binary",
                "Parquet physical type": "binary",
                "Logical type": None,
                "Notes": None
            },
            {
                "Type": "struct",
                "Parquet physical type": "group",
                "Logical type": None,
                "Notes": None
            },
            {
                "Type": "list",
                "Parquet physical type": "3-level list",
                "Logical type": "LIST",
                "Notes": "See Parquet docs for 3-level representation."
            },
            {
                "Type": "map",
                "Parquet physical type": "3-level map",
                "Logical type": "MAP",
                "Notes": "See Parquet docs for 3-level representation."
            },
        ]

    def iceberg_dtype_trino_map(self) -> dict:
        """
        Get data mapping from iceberg to trino

        :return: dictionary contains data mapping
        """

        return {
            "BOOLEAN": "BOOLEAN",
            "INT": "INTEGER",
            "LONG": "BIGINT",
            "FLOAT": "REAL",
            "DOUBLE": "DOUBLE",
            "DECIMAL(p,s)": "DECIMAL(p,s)",
            "DATE": "DATE",
            "TIME": "TIME(6)",
            "TIMESTAMP": "TIMESTAMP(6)",
            "TIMESTAMPTZ": "TIMESTAMP(6) WITH TIME ZONE",
            "STRING": "VARCHAR",
            "UUID": "UUID",
            "BINARY": "VARBINARY",
            "FIXED (L)": "VARBINARY",
            "STRUCT(...)": "ROW(...)",
            "LIST(e)": "ARRAY(e)",
            "MAP(k,v)": "MAP(k,v)"
        }

    @staticmethod
    def construct_values(row):
        return f"({','.join(map(lambda x: repr(x), row))})"

    def iceberg_insert_data(
        self,
        data: pd.DataFrame,
        schema: str,
        table: str,
    ) -> None:
        """
        Insert data from dataframe to Iceberg table

        :param data: dataframe contains data to insert
        :param schema: destination schema
        :param table: destination table
        """

        data = data.replace(np.nan, None)
        columns = data.columns.to_list()

        placeholders_cols = ', '.join(
            ['?'] * len(data.columns)
        )
        placeholders = ', '.join(
            [
                f'({placeholders_cols})' for _ in range(
                    len(data)
                )
            ]
        )
        insert_query = f"""
        INSERT INTO
            ice_sop.{schema}.{table} ({', '.join(columns)})
        VALUES
            {placeholders}
        """

        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(
                insert_query,
                tuple(
                    data.values.flatten()
                )
            )
            print(cur.fetchall())
            cur.close()
            conn.close()
        except Exception:
            cur.close()
            conn.close()
            raise

    def iceberg_upsert_data(
        self,
        data: pd.DataFrame,
        schema: str,
        table: str,
        on_columns: list,
        columns_to_update: list = None,
    ) -> None:
        """
        Upsert data from dataframe to Iceberg table

        :param data: dataframe contains data to upsert
        :param schema: destination schema
        :param table: destination table
        :param on_columns: list of columns to set match condition for update
        :param columns_to_update: list of columns to update values
            based on `on_columns`
        """

        conn = self.connect()
        cur = conn.cursor()
        now = str(
            datetime.datetime.now().timestamp()
        ).replace(
            '.',
            '',
        )

        # Create staging table for the destination table
        try:
            cur.execute(
                f"""
                CREATE TABLE
                    ice_sop.{schema}.{table}_stg_{now}
                AS
                    SELECT
                        *
                    FROM
                        ice_sop.{schema}.{table}
                    WITH NO DATA
                """
            )
        except Exception:
            cur.close()
            conn.close()
            raise

        # Insert new data to staging table
        try:
            self.iceberg_insert_data(
                data,
                schema,
                f'{table}_stg_{now}',
            )
        except Exception:
            cur.execute(
                f"""
                DROP TABLE
                    ice_sop.{schema}.{table}_stg_{now}
                """
            )
            cur.close()
            conn.close()
            raise

        # Merge data from staging table to destination table
        try:
            if not columns_to_update:
                columns_to_update = self.get_data(
                    f"""
                    SELECT
                        *
                    FROM
                        ice_sop.{schema}.{table}
                    LIMIT
                        0
                    """
                ).columns.to_list()
                columns_to_update = [
                    i for i in columns_to_update
                    if i not in on_columns
                ]
            insert_values_query = ', '.join(
                [
                    f'source.{i}' for i in columns_to_update
                ]
            )
            insert_query = f"""
            INSERT
                ({', '.join(columns_to_update)})
            VALUES
                ({insert_values_query})
            """
            update_query = ', '.join(
                [
                    f'{i} = source.{i}'
                    for i in columns_to_update
                ]
            )
            matched_query = ' AND '.join(
                [
                    f'sink.{i} = source.{i}'
                    for i in on_columns
                ]
            )
            merge_query = f"""
            MERGE INTO
                ice_sop.{schema}.{table} sink
            USING
                ice_sop.{schema}.{table}_stg_{now} source
            ON
                {matched_query}
            WHEN MATCHED
                THEN UPDATE SET
                    {update_query}
            WHEN NOT MATCHED
                THEN {insert_query}
            """
            cur.execute(merge_query)
            print(cur.fetchall())

            cur.execute(
                f"""
                DROP TABLE
                    ice_sop.{schema}.{table}_stg_{now}
                """
            )
            cur.close()
            conn.close()
        except Exception:
            cur.execute(
                f"""
                DROP TABLE
                    ice_sop.{schema}.{table}_stg_{now}
                """
            )
            cur.close()
            conn.close()
            raise
