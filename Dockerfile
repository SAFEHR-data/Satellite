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

# User definable arguments
ARG POSTGRES_USER=postgres
ARG POSTGRES_PASSWORD=postgres
ARG DATABASE_NAME=emap
ARG N_TABLE_ROWS=4
ARG INSERT_RATE=0.3
ARG UPDATE_RATE=0.2
ARG DELETE_RATE=0.1
ARG EMAP_BRANCH_NAME=main
ARG STAR_SCHEMA_NAME=star
ARG FAKER_SEED=0
ARG TIMEZONE="Europe/London"
ARG TAG="main"

ARG DEBIAN_FRONTEND=noninteractive

# OS setup
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    procps ca-certificates locales python3.9-dev python3-pip git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    sed -i '/en_GB.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

# Install package
COPY . /Satellite

RUN if [ -d "/Satellite/satellite" ] ; then \
      echo "Found satellite package. Not cloning"; \
    else \
      echo "Cloning Satellite repo on: $TAG" && \
      rm -rf /Satellite && \
      git clone --depth 1 --branch ${TAG} https://github.com/SAFEHR-data/Satellite.git ;\
    fi && \
    pip install --no-cache-dir --upgrade pip==22.3.1

WORKDIR /Satellite
RUN pip install --no-cache-dir . && \
    satellite print-db-create-command > /docker-entrypoint-initdb.d/create.sql && \
    satellite print-create-command >> /docker-entrypoint-initdb.d/create.sql

# Export the variables to the runtime of the container
ENV POSTGRES_USER ${POSTGRES_USER}
ENV POSTGRES_PASSWORD ${POSTGRES_PASSWORD}
ENV DATABASE_NAME ${DATABASE_NAME}
ENV EMAP_BRANCH_NAME ${EMAP_BRANCH_NAME}
ENV STAR_SCHEMA_NAME ${STAR_SCHEMA_NAME}
ENV FAKER_SEED ${FAKER_SEED}
ENV TIMEZONE ${TIMEZONE}
ENV INSERT_RATE ${INSERT_RATE}
ENV UPDATE_RATE ${UPDATE_RATE}
ENV DELETE_RATE ${DELETE_RATE}
ENV LANG=en_GB.UTF-8
ENV LC_ALL=en_GB.UTF-8

ENTRYPOINT ["./entrypoint.sh"]
