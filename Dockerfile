FROM postgres:15.0-bullseye

# Required envrionment variables
ARG POSTGRES_USER=postgres
ARG POSTGRES_PASSWORD=postgres
ARG N_TABLE_ROWS=2
ARG DEBIAN_FRONTEND=noninteractive

# OS setup
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    procps ca-certificates locales python3.9-dev python3-pip git  \
    gnupg libpq-dev g++ postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i '/en_GB.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

# Define github credentials to be able to clone the fake-star repo
ARG GIT_USER=
ARG GIT_PASSWORD=

# Create .sql file that will be used to initallly populate the database
RUN git clone https://${GIT_USER}:${GIT_PASSWORD}@github.com/UCLH-DIF/fake-star.git && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r fake_star/requirements.txt && \

WORKDIR /fake_data/fake_star/
RUN python print_sql_create_command.py > /docker-entrypoint-initdb.d/create.sql && \

# Clean up repo and Python
RUN rm -rf fake-star
RUN apt-get --purge autoremove python3.9 python3-pip
