import click

from satellite._log import logger
from satellite._fake import Faker
from satellite._database import Database
from satellite._tables import Tables
from satellite._settings import EnvVar


@click.group()
def cli() -> None:
    """Satellite command line interface"""


@cli.command()
def print_create_command() -> None:
    """
    Print an SQL table create command for an EMAP Star schema. Required environment
    variables:
        - INFORMDB_BRANCH_NAME
        - N_TABLE_ROWS
        - FAKER_SEED
        - STAR_SCHEMA_NAME
        - POSTGRES
    """
    db = Database(
        schema_name=EnvVar("STAR_SCHEMA_NAME").or_default(),
        username=EnvVar("POSTGRES_USER").unwrap()
    )

    tables = Tables.from_repo(
        repo_url="https://github.com/inform-health-informatics/Inform-DB",
        branch_name=EnvVar("INFORMDB_BRANCH_NAME").or_default(),
    )

    fake = Faker()
    Faker.seed(EnvVar("FAKER_SEED").unwrap_as(int))

    print(db.schema_create_command)

    for table in tables.topologically_sorted():
        print(db.empty_table_create_command_for(table))

        if table.n_rows > 0:
            table.add_fake_data(fake)
            print(db.add_data_command_for(table))

    logger.info("Successfully printed fake tables")
