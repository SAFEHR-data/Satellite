import git
import networkx as nx

from typing import List, Generator, Optional
from pathlib import Path
from faker import Faker

from satellite._utils import camel_to_snake_case
from satellite._settings import EnvVar
from satellite._log import logger
from satellite._column import Column
from satellite._fake import fake


class Row:
    def __init__(self, table_name: str, columns: List[Column]):
        self.table_name = table_name
        self.columns = columns
        self.values = []

    @classmethod
    def with_fake_values(cls, table_name: str, columns: List[Column]) -> "Row":
        row = cls(table_name=table_name, columns=columns)
        for col in row.columns:
            function = col.faker_method(fake)
            row.values.append(function())

        return row


class Table:
    """Single table in a Star schema"""

    def __init__(self, name: str):
        self.name = str(name)
        self.data = dict()  # Keyed with column names with a list of rows as a value
        self._extends_temporal_core = False
        self.n_rows = EnvVar("N_TABLE_ROWS").unwrap_as(int)

    @classmethod
    def from_java_file(cls, filepath: Path) -> "Table":
        logger.info(f"Creating table from {filepath.name}")

        self = Table(name=camel_to_snake_case(filepath.stem))

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

            column = Column(name=camel_to_snake_case(attr_name), java_type=java_type)

            self.data[column] = []

        return self

    def add_fake_data(self) -> None:
        logger.info(f"Adding fake data to {self.name}")

        for column, values in self.data.items():

            if column.name == self.primary_key_name:
                continue  # This is just a serial index so no need to create fake values

            logger.info(f"Creating random data for {column}")
            function = column.faker_method(fake)

            for _ in range(self.n_rows):
                values.append(function())

        return None

    def fake_row(self) -> Row:
        return Row.with_fake_values(table_name=self.name, columns=self.columns)

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


class Tables(list):
    """List of tables present in a star schema"""

    @classmethod
    def from_repo(cls, repo_url: str, branch_name: str) -> "Tables":
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

    def set_num_rows_from(self, schema: "DatabaseSchema") -> None:
        """Set the number of rows present in each table from a schema"""



