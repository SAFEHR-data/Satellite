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
import click

from satellite._log import logger
from satellite._schema import DatabaseSchema
from satellite._tables import Tables
from satellite._settings import EnvVar
from satellite._utils import call_every_n_seconds

PAT = EnvVar("INFORMDB_PAT").unwrap()
if PAT.startswith("github_pat"):  # is a fine-grained token
    REPO_URL = f"https://oauth2:{PAT}@github.com/UCLH-Foundry/Inform-DB"
else:
    REPO_URL = f"https://{PAT}:x-oauth-basic@github.com/UCLH-Foundry/Inform-DB"

star = DatabaseSchema(
    name=EnvVar("STAR_SCHEMA_NAME").or_default(),
    host=EnvVar("POSTGRES_HOST").or_default(),
    database_name=EnvVar("DATABASE_NAME").or_default(),
    username=EnvVar("POSTGRES_USER").unwrap(),
    password=EnvVar("POSTGRES_PASSWORD").unwrap(),
    tables=Tables.from_repo(
        repo_url=REPO_URL,
        branch_name=EnvVar("INFORMDB_BRANCH_NAME").or_default(),
    ),
)


@click.group()
def cli() -> None:
    """Satellite command line interface"""


@cli.command()
def print_db_create_command() -> None:
    print(f"CREATE DATABASE {star.database_name};")


@cli.command()
def print_create_command() -> None:
    """Print an SQL table create command for an EMAP Star schem"""

    print(star.schema_create_command)

    for table in star.tables.topologically_sorted():
        table.add_fake_data()
        print(star.empty_table_create_command_for(table))
        print(star.add_data_command_for(table))

    logger.info("Successfully printed fake tables")


@cli.command()
@click.option(
    "--max-num-rows",
    default=1e8,
    type=int,
    help="Number of rows above which no more are inserted",
)
def continuously_insert(max_num_rows: int) -> None:
    """
    Continuously run row inserts into all tables at a frequency defined by INSERT_RATE
    in rows per seconds
    """
    try:
        time_delay = 1 / EnvVar("INSERT_RATE").unwrap_as(float)
    except ZeroDivisionError:
        logger.info("Not inserting any rows. Insert rate was zero")
        return

    logger.info(f"Running continuous inserts every {time_delay} seconds")

    def insert() -> None:
        star.update_num_rows_in_tables()
        for table in star.tables.topologically_sorted():

            if table.n_rows < max_num_rows:
                star.insert(table.fake_row())

    call_every_n_seconds(insert, num_seconds=time_delay)


@cli.command()
def continuously_update() -> None:
    """
    Continuously run row updates into all tables at a frequency defined by UPDATE_RATE
    in rows per seconds
    """
    try:
        time_delay = 1 / EnvVar("UPDATE_RATE").unwrap_as(float)
    except ZeroDivisionError:
        logger.info("Not updating any rows. Update rate was zero")
        return

    logger.info(f"Running continuous updates every {time_delay} seconds")

    def update() -> None:
        star.update_num_rows_in_tables()
        for table in star.tables:
            logger.debug(f"Updating row from {table.name}")
            star.update(table.randomised_existing_row())

    call_every_n_seconds(update, num_seconds=time_delay)


@cli.command()
def continuously_delete() -> None:
    """
    Continuously run row deletes into all tables at a frequency defined by DELETE_RATE
    in rows per seconds
    """
    try:
        time_delay = 1 / EnvVar("DELETE_RATE").unwrap_as(float)
    except ZeroDivisionError:
        logger.info("Not deleting any rows. Delete rate was zero")
        return

    logger.info(f"Running continuous deletes every {time_delay} seconds")

    def delete() -> None:
        star.update_num_rows_in_tables()
        for table in star.tables:
            logger.debug(f"Deleting row from {table.name}")
            star.delete(table.random_existing_row())

    call_every_n_seconds(delete, num_seconds=time_delay)


@cli.command()
def schema_exists() -> None:
    return print(star.exists)
