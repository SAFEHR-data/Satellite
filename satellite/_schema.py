import psycopg2
from typing import Optional, Any

from satellite._log import logger
from satellite._tables import Row, Table, Tables


class DatabaseSchema:
    """Database containing a fake EMAP star schema"""

    def __init__(
        self,
        name: str,
        tables: Tables,
        host: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.tables = tables
        self._name = name
        self._host = host
        self._username = username
        self._password = password

        self._cursor: Any = None
        self._connection: Any = None
        self._try_and_connect()

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
            f"DROP SCHEMA IF EXISTS {self.schema_name} CASCADE;\n"
            f"CREATE SCHEMA {self.schema_name} "
            f"AUTHORIZATION {self._username};\n"
        )

    @property
    def exists(self) -> bool:
        """Does this schema exist in the database?"""
        if self._connection is None or bool(self._connection.closed):
            return False

        result = self._execute_and_fetch(
            f"SELECT schema_name FROM information_schema.schemata "
            f"  WHERE schema_name = '{self.schema_name}';"
        )
        return self.schema_name in result

    def _try_and_connect(self) -> None:
        try:
            self._connection = psycopg2.connect(
                f"dbname=postgres user={self._username} "
                f"password={self._password} host={self._host}"
            )
            self._cursor = self._connection.cursor()
        except psycopg2.OperationalError:
            pass

    def empty_table_create_command_for(self, table: Table) -> str:
        """Create a table for a set of data. Drop it if it exists"""

        columns_name_and_type = ", ".join(
            [col.definition_in_schema(self._name) for col in table.columns]
        )
        return (
            f"CREATE TABLE {self.schema_name}.{table.name} "
            f"({table.primary_key_name} serial PRIMARY KEY, "
            f"{columns_name_and_type});"
        )

    def add_data_command_for(self, table: Table) -> str:
        """Addd a table to the schema"""
        if table.n_rows == 0:
            logger.debug(f"Not adding any data to {table}. n_rows == 0")
            return ""

        logger.info(f"Adding table data: {table.name}")

        string = ""
        col_names = ",".join(col.name for col in table.columns)

        string += (
            f"  INSERT INTO {self.schema_name}.{table.name} ({col_names}) VALUES \n"
        )

        for i in range(table.n_rows):

            values = ",".join(
                column.format_specifier % table.data[column][i]
                for column in table.columns
            )
            string += f"  ({values}),\n"

        return string.rstrip(",\n") + ";"

    def _execute(self, query: str, values: Optional[list] = None) -> None:
        self._cursor.execute(query=query, vars=values)

    def _execute_and_fetch(self, query: str, values: Optional[list] = None) -> tuple:
        self._execute(query, values)
        return tuple(self._cursor.fetchone())

    def insert(self, row: Row) -> None:
        """Insert a single row from a table"""
        assert self.exists
        column_names = ", ".join(column.name for column in row.columns)
        value_definitions = ",".join("%s" for _ in range(len(row.values)))

        self._execute(
            f"INSERT INTO {self.schema_name}.{row.table_name} "
            f"({column_names}) VALUES ({value_definitions})",
            values=[value for value in row.values]
        )
        self._connection.commit()

    def update_num_rows_in_tables(self) -> None:
        """Set the number of rows in each table"""
        assert self.exists
        logger.info("Setting the number of rows present in each table")

        for table in self.tables:
            table.n_rows = self._execute_and_fetch(
                f"SELECT COUNT(*) FROM {self.schema_name}.{table.name}"
            )[0]
            logger.info(f"{table.name} has {table.n_rows} rows")
