from typing import Optional
from dataclasses import dataclass

from satellite._settings import EnvVar
from satellite._log import logger


@dataclass
class Column:
    name: str
    java_type: str
    table_reference: Optional["Table"] = None

    @property
    def sql_type(self) -> str:

        java_to_sql_type_map = {
            "long": "bigint",
            "string": "text",
            "instant": "timestamptz",
            "boolean": "boolean",
            "double": "real",
            "localdate": "date",
            "byte[]": "bytea",
        }

        if self.java_type.lower() in java_to_sql_type_map:
            return java_to_sql_type_map[self.java_type.lower()]
        else:
            logger.error(
                f"Failed to determine the derived type from {self.java_type} "
                f"for {self.name}, defaulting to text"
            )
            return "text"

    def __hash__(self):
        return hash(self.name)

    @property
    def format_specifier(self) -> str:
        if self.sql_type == "text":
            return "'%s'"
        elif self.sql_type == "timestamptz" or self.sql_type == "date":
            return "timestamp '%s'"
        elif self.sql_type == "bytea":
            return "E'%s'"

        return "%s"

    @property
    def is_foreign_key(self) -> bool:
        return self.table_reference is not None

    def definition_in_schema(self, schema_name: str) -> str:
        """Return a string containing the name, type and references to other tables"""
        ref_str = (
            ""
            if self.table_reference is None
            else f" REFERENCES {schema_name}.{self.table_reference.name}"
        )
        return f"{self.name} {self.sql_type}{ref_str}"
