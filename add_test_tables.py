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
from constants import *
from dataclasses import dataclass
from pathlib import Path


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
        # TODO
        raise NotImplementedError

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

        # If a line includes any of these characters it will be skipped
        excluded_chars = ("@", "*", "(", "=")

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
                    or any(char in line for char in excluded_chars)
                    or not any(s in line for s in delc_strings)):
                continue

            java_type, attr_name = line.split()[-2:]

            # All attributes that end with Id are foreign keys, thus just ints
            if attr_name.endswith("Id"):
                java_type = "Long"

            column = Column(
                name=_camel_to_snake_case(attr_name.rstrip(";")),
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

            for _ in range(self.n_rows):

                try:
                    value = getattr(fake, column.name)()
                except AttributeError:
                    value = fake.bothify("??????")  # Random string

                values.append(value)

        return None


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
        return pypg.connect(connection_string)


class FakeDatabase(Database):
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

        cols = ",".join([table.col_name_to_name_and_sql_type(c)
                         for c in table.columns])

        self._cursor.execute(
            f"CREATE TABLE {self.schema_name}.{table.name}"
            f"({table.name}_id serial PRIMARY KEY, {cols});"
        )

    def add(self, table: Table) -> None:
        """Addd a table to the schema"""
        print(f"Adding table: {table.name}")
        self.create_empty_table_for(table)

        cols = ",".join(table.columns)
        vals = ",".join("%s" for _ in range(len(table.columns)))

        for _, row in table.astype('object').iterrows():

            self._cursor.execute(
                f"INSERT INTO {self.schema_name}.{table.name} ({cols}) VALUES ({vals})",
                row.values,
            )

        self._connection.commit()


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

    # db = FakeDatabase()
    # db.create_schema()

    tables = StarTables.from_repo(
        repo_url="https://github.com/inform-health-informatics/Inform-DB",
        branch_name=branch
    )

    for table in tables:
        table.add_fake_data()
        print(table.data)
        break
        # db.add(table)

    print("Successfully created fake tables!")
    return None


if __name__ == "__main__":
    main()
