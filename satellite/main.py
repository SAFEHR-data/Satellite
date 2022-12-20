import click

from satellite._log import logger
from satellite._schema import DatabaseSchema
from satellite._tables import Tables
from satellite._settings import EnvVar
from satellite._utils import call_every_n_seconds


star = DatabaseSchema(
    name=EnvVar("STAR_SCHEMA_NAME").or_default(),
    host=EnvVar("POSTGRES_HOST").or_default(),
    username=EnvVar("POSTGRES_USER").unwrap(),
    password=EnvVar("POSTGRES_PASSWORD").unwrap(),
    tables=Tables.from_repo(
        repo_url="https://github.com/inform-health-informatics/Inform-DB",
        branch_name=EnvVar("INFORMDB_BRANCH_NAME").or_default(),
    )
)


@click.group()
def cli() -> None:
    """Satellite command line interface"""


@cli.command()
def print_create_command() -> None:
    """
    Print an SQL table create command for an EMAP Star schema. Required environment
    variables:
        - N_TABLE_ROWS
        - FAKER_SEED
        - STAR_SCHEMA_NAME
        - POSTGRES_USER
    """
    logger.info("Printing schema + table create commands")
    print(star.schema_create_command)

    for table in star.tables.topologically_sorted():
        table.add_fake_data()
        print(star.empty_table_create_command_for(table))
        print(star.add_data_command_for(table))

    logger.info("Successfully printed fake tables")


@cli.command()
def continuously_insert() -> None:
    """
    Continuously run row inserts into all tables at a frequency defined by INSERT_RATE
    in rows per seconds. Required environment variables:
        - POSTGRES_HOST
        - POSTGRES_USER
        - POSTGRES_PASSWORD
        - INSERT_RATE
        - FAKER_SEED
    """
    time_delay = 1 / EnvVar("INSERT_RATE").unwrap_as(float)
    logger.info(f"Running continuous inserts every {time_delay} seconds")

    def insert() -> None:
        star.update_num_rows_in_tables()
        for table in star.tables:
            star.insert(table.fake_row())

    call_every_n_seconds(insert, num_seconds=time_delay)
