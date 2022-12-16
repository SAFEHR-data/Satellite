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
import os
import re
import git
import logging
import coloredlogs
import faker
import networkx as nx

from faker.providers import BaseProvider
from faker.providers.date_time import Provider as FakerDTProvider
from datetime import datetime, date
from dataclasses import dataclass
from typing import List, Optional, Generator
from pathlib import Path


logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO, logger=logger)


def _env_var(key: str) -> str:
    """Get an environment variable and raise a helpful exception if it's not"""

    if (value := os.environ.get(key, None)) is None:
        raise RuntimeError(
            f"Failed to find ${key}. Ensure it is set as " f"an environment variable"
        )
    return value


# from: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
_camel_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def _camel_to_snake_case(string: str) -> str:
    return _camel_case_pattern.sub("_", string).lower()


class Faker(faker.Faker):
    """Custom Faker"""

    @classmethod
    def with_providers(cls, *providers):
        """Create a Faker instance with a set of providers"""

        self = cls()
        for provider in providers:
            self.add_provider(provider)

        return self


class StarBaseProvider(BaseProvider):
    """
    Provider for fake data in an EMAP star schema.
    The provider methods must be named as snake_case version of the
    column names or as the postgres sql types that will be used, the
    latter used as a fallback
    """

    @staticmethod
    def default() -> str:
        return ""

    def mrn(self) -> str:
        return self.bothify("#########")

    def bigint(self) -> int:
        return self.random_int()

    def text(self) -> str:
        return self.bothify("?????")

    def boolean(self) -> bool:
        return bool(self.random_int(0, 1))

    def real(self) -> float:
        return float(self.random_int(0, 1000)) / 100.0

    def bytea(self) -> str:
        return self.text()  # Encoding happens in the format specifier


class StarDatetimeProvider(FakerDTProvider):
    def timestamptz(self) -> datetime:
        return self.date_time()

    def date(self) -> date:
        return self.date_between(
            date.fromisoformat("1970-01-01"), date.fromisoformat("2022-01-01")
        )


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

    @property
    def sql_definition(self) -> str:
        """Return a string containing the name, type and references to other tables"""
        schema_name = _env_var("STAR_SCHEMA_NAME")
        ref_str = (
            ""
            if self.table_reference is None
            else f" REFERENCES {schema_name}.{self.table_reference.name}"
        )
        return f"{self.name} {self.sql_type}{ref_str}"


class Table:
    def __init__(self, name: str):
        self.name = str(name)
        self.data = dict()  # Keyed with column names with a list of rows as a value
        self._extends_temporal_core = False

    @classmethod
    def from_java_file(cls, filepath: Path) -> "Table":
        logger.info(f"Creating table from {filepath.name}")

        self = Table(name=_camel_to_snake_case(filepath.stem))

        passed_class_definition = False

        # If a line includes any of these substrings it will be skipped
        # note all Lists are e.g. one<->many relationships
        excluded_substrings = ("@", "*", "(", "=", "List")

        # Strings that define if a class attribute is being defined
        delc_strings = ("private", "public", "protected")
        depth = 0

        for line in open(filepath, "r"):

            if "{" in line:
                depth += 1

            if "}" in line:
                depth -= 1

            if f"class {filepath.stem}" in line:
                self._extends_temporal_core = "extends TemporalCore" in line
                passed_class_definition = True
                continue

            if (
                not passed_class_definition
                or depth != 1
                or any(s in line for s in excluded_substrings)
                or not any(s in line for s in delc_strings)
            ):
                continue

            # e.g. line = "private Instant storedFrom;"
            line = line.strip().rstrip(";")
            java_type, attr_name = line.split()[-2:]

            # All attributes that end with Id are foreign keys, thus just ints
            if attr_name.endswith("Id"):
                java_type = "Long"

            column = Column(name=_camel_to_snake_case(attr_name), java_type=java_type)

            self.data[column] = []

        return self

    @property
    def n_rows(self) -> int:
        # TODO: more granular configuration
        return int(_env_var("N_TABLE_ROWS"))

    def add_fake_data(self, fake: Faker) -> None:
        logger.info(f"Adding fake data to {self.name}")

        for column, values in self.data.items():

            if column.name == self.primary_key_name:
                continue  # This is just a serial index so no need to create fake values

            logger.info(f"Creating random data for {column}")

            if hasattr(fake, column.name):  # match for specific column e.g. mrn
                faker_method = getattr(fake, column.name)

            elif column.is_foreign_key:

                def _foreign_key_id():
                    return fake.pyint(1, column.table_reference.n_rows)

                faker_method = _foreign_key_id

            elif hasattr(fake, column.sql_type):  # match for the type of column
                faker_method = getattr(fake, column.sql_type)

            else:
                logger.error(f"Have no provider for {column.sql_type}")
                faker_method = fake.default

            logger.debug(f"   using {faker_method}")
            for _ in range(self.n_rows):
                values.append(faker_method())

        return None

    def add_columns_from(self, table: "Table") -> None:
        """Add a set of columns to this table from another table"""
        for column in table.columns:
            self.data[column] = []

    def assign_foreign_keys(self, tables: "StarTables") -> None:
        """
        Given the columns present in this table determine those that are
        foreign keys
        """
        for column in self.columns:
            try:
                column.table_reference = next(
                    table for table in tables if f"{table.name}_id" == column.name
                )
            except StopIteration:
                continue  # Not a foreign key referencing another tables PK

    @property
    def columns(self) -> List[Column]:
        return [
            column
            for column in self.data.keys()
            if column.name != self.primary_key_name
        ]

    @property
    def primary_key_name(self) -> str:
        return f"{self.name}_id"

    @property
    def extends_temporal_core(self) -> bool:
        """Does this table extend i.e. have columns from a temporal core superclass?"""
        return self._extends_temporal_core


class FakeStarDatabase:
    """Fake database wrapper"""

    @property
    def schema_name(self) -> str:
        return _env_var("STAR_SCHEMA_NAME")

    @property
    def schema_create_command(self) -> str:
        """Create the database schema"""

        return (
            f"DROP SCHEMA IF EXISTS {self.schema_name} CASCADE;\n"
            f"CREATE SCHEMA {self.schema_name} "
            f"AUTHORIZATION {_env_var('POSTGRES_USER')};\n"
        )

    def empty_table_create_command_for(self, table: Table) -> str:
        """Create a table for a set of data. Drop it if it exists"""

        columns_name_and_type = ", ".join([c.sql_definition for c in table.columns])
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


class StarTables(list):
    """List of tables present in a star schema"""

    @classmethod
    def from_repo(cls, repo_url: str, branch_name: str) -> "StarTables":
        """Create a list of tables by traversing files from a cloned git repo"""
        excluded_suffixes = ["Core.java", "info.java", "TemporalFrom.java"]
        repo_path = Path("star_repo")

        if not repo_path.exists():
            logger.info(f"Cloning {repo_path}")
            _ = git.Repo.clone_from(url=repo_url, to_path=repo_path, branch=branch_name)

        self = cls()
        temporal_core_superclass = Table(name="temporal_core")

        for path in Path("star_repo/inform-db/src/main").rglob("**/*.java"):

            if path.name.endswith("TemporalCore.java"):
                temporal_core_superclass = Table.from_java_file(path)
                continue

            if any(path.name.endswith(suffix) for suffix in excluded_suffixes):
                continue

            self.append(Table.from_java_file(path))

        for table in self:
            table.assign_foreign_keys(self)
            if table.extends_temporal_core:
                table.add_columns_from(temporal_core_superclass)

        logger.info(f"Created {len(self)} tables from repo")
        return self

    def topologically_sorted(self) -> Generator:
        """Tables in topologically sorted order given the foreign key references"""

        dag = nx.DiGraph()
        dag.add_nodes_from(range(len(self)))
        for i, table in enumerate(self):
            for column in [col for col in table.columns if col.is_foreign_key]:
                dag.add_edge(i, self.index(column.table_reference))

        for node in reversed(list(nx.topological_sort(dag))):
            yield self[int(node)]


def main():

    db = FakeStarDatabase()

    tables = StarTables.from_repo(
        repo_url="https://github.com/inform-health-informatics/Inform-DB",
        branch_name=_env_var("INFORMDB_BRANCH_NAME"),
    )

    fake = Faker.with_providers(StarBaseProvider, StarDatetimeProvider)
    Faker.seed(_env_var("FAKER_SEED"))

    print(db.schema_create_command)

    for table in tables.topologically_sorted():
        print(db.empty_table_create_command_for(table))

        if table.n_rows > 0:
            table.add_fake_data(fake)
            print(db.add_data_command_for(table))

    logger.info("Successfully printed fake tables")
    return None


if __name__ == "__main__":
    main()
