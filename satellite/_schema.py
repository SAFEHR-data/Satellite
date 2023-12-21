#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
import psycopg2
from psycopg2 import IntegrityError
from typing import Optional, Any

from satellite._log import logger
from satellite._tables import Row, ExistingRow, Table, Tables


class DatabaseSchema:
    """Database containing a fake EMAP star schema"""

    def __init__(
        self,
        name: str,
        tables: Tables,
        database_name: str,
        host: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.tables = tables
        self._name = name
        self._host = host
        self._database_name = database_name
        self._username = username
        self._password = password

        self._cursor: Any = None
        self._connection: Any = None
        self._try_and_connect()

    @property
    def database_name(self) -> str:
        return self._database_name

    @property
    def schema_name(self) -> str:
        return self._name

    @property
    def schema_create_command(self) -> str:
        """Create the database schema"""
        if self._username is None:
            raise RuntimeError(
                "Cannot return a schema create command without "
                "a defined username for authorisation"
            )
        return (
            rf"\connect {self.database_name}" + "\n"
            f"DROP SCHEMA IF EXISTS {self.schema_name} CASCADE; \n"
            f"CREATE SCHEMA {self.schema_name} "
            f"AUTHORIZATION {self._username}; \n"
        )

    @property
    def exists(self) -> bool:
        """Does this schema exist in the database?"""
        if self._connection is None or bool(self._connection.closed):
            return False

        result = self._execute_and_fetch(
            f"SELECT schema_name FROM information_schema.schemata "
            f"  WHERE schema_name = '{self.schema_name}'; "
        )
        return self.schema_name in result

    def _try_and_connect(self) -> None:
        try:
            self._connection = psycopg2.connect(
                f"dbname={self._database_name} user={self._username} "
                f"password={self._password} host={self._host}"
            )
            self._cursor = self._connection.cursor()
        except psycopg2.OperationalError:
            pass

    def empty_table_create_command_for(self, table: Table) -> str:
        """Create a table for a set of data. Drop it if it exists"""

        columns_name_and_type = ", ".join(
            [col.definition_in_schema(self._name) for col in table.non_pk_columns]
        )
        return (
            f"CREATE TABLE {self.schema_name}.{table.name} "
            f"({table.primary_key_name} serial PRIMARY KEY, "
            f"{columns_name_and_type});"
        )

    @staticmethod
    def _decode_if_bytes(value: Any) -> Any:
        return value.decode() if isinstance(value, bytes) else value

    def add_data_command_for(self, table: Table) -> str:
        """Addd a table to the schema"""
        if table.n_rows == 0:
            logger.debug(f"Not adding any data to {table}. n_rows == 0")
            return ""

        logger.info(f"Adding table data: {table.name}")

        column_names = ",".join(col.name for col in table.non_pk_columns)
        string = (
            f"  INSERT INTO {self.schema_name}.{table.name} ({column_names}) VALUES \n"
        )

        for i in range(table.n_rows):
            values = ",".join(
                column.format_specifier % self._decode_if_bytes(table[column][i])
                if table[column][i] is not None
                else "null"
                for column in table.non_pk_columns
            )
            string += f"  ({values}), \n"

        return string.rstrip(",\n") + ";"

    def _execute(self, query: str, values: Optional[list] = None) -> None:
        try:
            self._cursor.execute(query=query, vars=values)
        except IntegrityError as e:
            logger.warning(f"Failed to execute due to: \n{e}")
            self._connection.rollback()

    def _execute_and_fetch(self, query: str, values: Optional[list] = None) -> tuple:
        self._execute(query, values)
        return tuple(self._cursor.fetchone())

    def _execute_and_commit(self, query: str, values: Optional[list] = None) -> None:
        self._execute(query=query, values=values)
        self._connection.commit()

    def insert(self, row: Row) -> None:
        """Insert a single row from a table"""
        assert self.exists
        column_names = ", ".join(column.name for column in row.non_pk_columns)
        value_definitions = ",".join("%s" for _ in range(len(row.non_pk_columns)))

        self._execute_and_commit(
            f"INSERT INTO {self.schema_name}.{row.table_name} "
            f"({column_names}) VALUES ({value_definitions})",
            values=[row[column] for column in row.non_pk_columns],
        )

    def update(self, row: ExistingRow) -> None:
        """Update the values in a row that exists in a table already"""
        assert self.exists and row.id is not None
        if len(row.data_columns) == 0:
            return  # Nothing to be updated

        col_names_and_format = ",".join(f"{c.name} = %s" for c in row.data_columns)

        self._execute_and_commit(
            f"UPDATE {self.schema_name}.{row.table_name} SET {col_names_and_format} "
            f"WHERE {row.pk_column.name} = {row.id}; ",
            values=[row[column] for column in row.data_columns],
        )

    def delete(self, row: ExistingRow) -> None:
        """Delete a row that exists in the schema"""
        assert self.exists

        if row.id is None:
            logger.warning("Primary key for delete was unspecified - skipping")
            return

        self._execute_and_commit(
            f"DELETE FROM {self.schema_name}.{row.table_name} "
            f"WHERE {row.pk_column.name} = {row.id}; "
        )

    def update_num_rows_in_tables(self) -> None:
        """Set the number of rows in each table"""
        assert self.exists
        logger.info("Setting the number of rows present in each table")

        for table in self.tables:
            table.n_rows = self._execute_and_fetch(
                f"SELECT COUNT(*) FROM {self.schema_name}.{table.name}"
            )[0]
            logger.info(f"{table.name} has {table.n_rows} rows")
