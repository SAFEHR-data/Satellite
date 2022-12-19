from typing import Optional

from satellite._log import logger
from satellite._tables import Table


class Database:
    """Database containing a fake EMAP star schema"""

    def __init__(
            self,
            schema_name: str = "star",
            host: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
    ):
        self._schema_name = schema_name
        self._host = host
        self._username = username
        self._password = password

    @property
    def schema_name(self) -> str:
        return self._schema_name

    @property
    def schema_create_command(self) -> str:
        """Create the database schema"""
        if self._username is None:
            raise RuntimeError("Cannot return a schema create command without "
                               "a defined username for authorisation")
        return (
            f"DROP SCHEMA IF EXISTS {self.schema_name} CASCADE;\n"
            f"CREATE SCHEMA {self.schema_name} "
            f"AUTHORIZATION {self._username};\n"
        )

    def empty_table_create_command_for(self, table: Table) -> str:
        """Create a table for a set of data. Drop it if it exists"""

        columns_name_and_type = ", ".join(
            [col.definition_in_schema(self._schema_name) for col in table.columns]
        )
        return (
            f"CREATE TABLE {self.schema_name}.{table.name} "
            f"({table.primary_key_name} serial PRIMARY KEY, "
            f"{columns_name_and_type});"
        )

    def add_data_command_for(self, table: Table) -> str:
        """Addd a table to the schema"""
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

