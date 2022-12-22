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
from typing import Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass

from satellite._log import logger

if TYPE_CHECKING:
    from satellite._tables import Table
    from satellite._fake import _Faker


@dataclass
class Column:
    name: str
    java_type: str
    parent_table_name: str  # Table in which this column is present
    table_reference: Optional["Table"] = None  # Table referenced by a foreign key

    def __hash__(self):
        return hash(self.name + self.parent_table_name)

    def __repr__(self):
        string = f"Column({self.name}, type={self.sql_type} "
        string += f"parent_table={self.parent_table_name}"
        string += (
            ""
            if self.table_reference is None
            else f", table_reference={self.table_reference.name}"
        )
        return string

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
        return not self.is_primary_key and self.table_reference is not None

    @property
    def is_primary_key(self) -> bool:
        return self.name == f"{self.parent_table_name}_id"

    def definition_in_schema(self, schema_name: str) -> str:
        """Return a string containing the name, type and references to other tables"""
        ref_str = (
            ""
            if self.table_reference is None
            else f" REFERENCES {schema_name}.{self.table_reference.name}"
        )
        return f"{self.name} {self.sql_type}{ref_str}"

    def faker_method(self, fake: "_Faker") -> Callable:
        """Faker method to generate synthetic/fake values for this column"""

        if self.is_primary_key:
            return lambda: None

        elif hasattr(fake, self.name):  # match for specific column e.g. mrn
            return getattr(fake, self.name)

        elif self.is_foreign_key:
            return lambda: fake.pyint(1, self.table_reference.n_rows)

        elif hasattr(fake, self.sql_type):  # match for the type of column
            return getattr(fake, self.sql_type)

        else:
            logger.error(f"Have no provider for {self.sql_type}")
            return fake.default
