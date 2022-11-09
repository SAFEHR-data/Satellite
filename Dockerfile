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
FROM postgres:15.0-bullseye

# Required envrionment variables
ARG POSTGRES_USER=postgres
ARG POSTGRES_PASSWORD=postgres
ARG N_TABLE_ROWS=2
ARG DEBIAN_FRONTEND=noninteractive
ARG INFORMDB_BRANCH_NAME=develop
ARG STAR_SCHEMA_NAME=star
ARG FAKER_SEED=0

# OS setup
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    procps ca-certificates locales python3.9-dev python3-pip git  \
    gnupg libpq-dev g++ postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i '/en_GB.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

# Define github credentials to be able to clone the fake-star repo
ARG GIT_USER
ARG GIT_PASSWORD

# Create .sql file that will be used to initallly populate the database
RUN git clone https://${GIT_USER}:${GIT_PASSWORD}@github.com/UCLH-DIF/fake-star.git && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r fake-star/requirements.txt

WORKDIR /fake-star/
RUN git checkout t-young31/issue4  # TODO: remove
RUN python3.9 print_sql_create_command.py > /docker-entrypoint-initdb.d/create.sql && \

# Clean up repo and Python
RUN rm -rf /fake-star
RUN apt-get --purge autoremove python3.9 python3-pip
