"""
Adds fake data to a database resembling the EMAP star scheme, albeit a
truncated version. A postgres instance should be up and running before running
this script, which requires environment variables (e.g. STAR_USER) to be
set
"""
import os
import re
import click
import git
import psycopg2 as pypg
import logging
import coloredlogs

from fake import fake
from dataclasses import dataclass
from typing import List
from pathlib import Path


N_TABLE_ROWS = {
    "default": 2,
    # Add table names here (snake_case) with associated sizes
}


logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO, logger=logger)


def _env_var(key: str) -> str:
    """Get an environment variable and raise a helpful exception if it's not"""

    if (value := os.environ.get(key, None)) is None:
        raise RuntimeError(f"Failed to find ${key}. Ensure it is set as "
                           f"an environment variable")
    return value


# from: https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
_camel_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')


def _camel_to_snake_case(string: str) -> str:
    return _camel_case_pattern.sub('_', string).lower()


@dataclass
class Column:
    name: str
    java_type: str

    @property
    def sql_type(self) -> str:

        java_to_sql_type_map = {
            "long": "bigint",
            "string": "text",
            "instant": "timestamptz",
            "boolean": "boolean",
            "double": "real",
            "localdate": "date",
            "byte[]": "bytea"
        }

        if self.java_type.lower() in java_to_sql_type_map:
            return java_to_sql_type_map[self.java_type.lower()]
        else:
            logger.error(f"Failed to determine the derived type from {self.java_type} "
                         f"for {self.name}, defaulting to text")
            return "text"

    def __hash__(self):
        return hash(self.name)


class Table:

    def __init__(self, name: str):
        self.name = str(name)
        self.data = dict()  # Keyed with column names with a list of rows as a value

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

            if f"public class {filepath.stem}" in line:
                passed_class_definition = True
                continue

            if (not passed_class_definition
                    or depth != 1
                    or any(s in line for s in excluded_substrings)
                    or not any(s in line for s in delc_strings)):
                continue

            # e.g. line = "private Instant storedFrom;"
            line = line.strip().rstrip(";")
            java_type, attr_name = line.split()[-2:]

            # All attributes that end with Id are foreign keys, thus just ints
            if attr_name.endswith("Id"):
                java_type = "Long"

            column = Column(
                name=_camel_to_snake_case(attr_name),
                java_type=java_type
            )

            self.data[column] = []

        return self

    @property
    def n_rows(self) -> int:
        if self.name in N_TABLE_ROWS:
            return N_TABLE_ROWS[self.name]
        else:
            return N_TABLE_ROWS["default"]

    def add_fake_data(self) -> None:
        logger.info(f"Adding fake data to {self.name}")

        for column, values in self.data.items():
            logger.info(f"Creating random data for {column}")

            if hasattr(fake, column.name):        # match for specific column e.g. mrn
                faker_method = getattr(fake, column.name)

            elif hasattr(fake, column.sql_type):  # match for the type of column
                faker_method = getattr(fake, column.sql_type)
            else:
                faker_method = fake.default       # Random string

            for _ in range(self.n_rows):
                values.append(faker_method())

        return None

    @property
    def columns(self) -> List[Column]:
        return list(self.data.keys())


class Database:
    """Fake database wrapper"""

    def __init__(self):

        self._connection = self._create_connection()
        self._cursor = self._connection.cursor()

    @staticmethod
    def _create_connection() -> "psycopg2.connection":

        connection_string = (
            f"dbname={_env_var('STAR_DB_NAME')} "
            f"user={_env_var('STAR_USER')} "
            f"password={_env_var('STAR_PASSWORD')} "
            f"host={_env_var('STAR_HOST')}"
        )
        print(connection_string)
        return pypg.connect(connection_string)


class FakeStarDatabase(Database):
    """Fake database wrapper"""

    @property
    def schema_name(self) -> str:
        return _env_var("STAR_SCHEMA_NAME")

    def create_schema(self) -> None:
        """Create the database schema"""

        self._cursor.execute(f"DROP SCHEMA IF EXISTS {self.schema_name} CASCADE;")
        self._cursor.execute(f"CREATE SCHEMA {self.schema_name}"
                             f" AUTHORIZATION {_env_var('STAR_USER')};")

    def create_empty_table_for(self, table: Table) -> None:
        """Create a table for a set of data. Drop it if it exists"""

        cols = ",".join([f"{c.name} {c.sql_type}" for c in table.columns])

        self._cursor.execute(
            f"CREATE TABLE {self.schema_name}.{table.name} ({cols});"
        )

    def add(self, table: Table) -> None:
        """Addd a table to the schema"""
        logger.info(f"Adding table: {table.name}")
        self.create_empty_table_for(table)

        for column in table.columns:

            for value in table.data[column]:
                self._cursor.execute(
                    f"INSERT INTO {self.schema_name}.{table.name} "
                    f"({column.name}) VALUES (%s)",
                    [value]
                )

        self._connection.commit()
        return None


class StarTables(list):
    """List of tables present in a star schema"""

    @classmethod
    def from_repo(cls, repo_url: str, branch_name: str) -> "StarTables":
        """Create a list of tables by traversing files from a cloned git repo"""
        excluded_suffixes = ["Core.java", "info.java", "TemporalFrom.java"]
        repo_path = Path("star_repo")

        if not repo_path.exists():
            logger.info(f"Cloning {repo_path}")
            _ = git.Repo.clone_from(
                url=repo_url,
                to_path=repo_path,
                branch=branch_name
            )

        self = cls()

        for path in Path("star_repo/inform-db/src/main").rglob(f"**/*.java"):
            if any(path.name.endswith(suffix) for suffix in excluded_suffixes):
                continue

            self.append(Table.from_java_file(path))

        logger.info(f"Created {len(self)} tables from repo")
        return self


@click.command()
@click.option(
    "--branch",
    type=str,
    default="develop",
    help="Branch of Inform-DB to clone"
)
def main(branch: str):

    db = FakeStarDatabase()
    db.create_schema()

    tables = StarTables.from_repo(
        repo_url="https://github.com/inform-health-informatics/Inform-DB",
        branch_name=branch
    )

    for table in tables:
        table.add_fake_data()
        db.add(table)

    logger.info("Successfully created fake tables!")
    return None


if __name__ == "__main__":
    main()
