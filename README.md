# Satellite

> **Warning**
> This requires access to the private Inform-DB repository defining the EMAP star schema

Satellite is a Python package for creating and populating an
[EMAP star](https://github.com/inform-health-informatics/Inform-DB) schema
with completely synthetic/fake data.

The `Dockerfile` is suitable to build a postgres instance directly but requires
a GitHub [PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
with access to the Inform-DB repository. Run as a single container:
```bash
docker build . -t satellite --build-arg GITHUB_PAT=<ghb_XXXXX>
docker run -it -p 5432:5432 satellite
```

Use in a Docker compose file:
```yaml
version: "3.9"

services:
  star:
    image: satellite
    container_name: fake_star_db
    build:
      context: .
      dockerfile: Dockerfile
      args:
        POSTGRES_USER: postgres      # Username to access the database
        POSTGRES_PASSWORD: postgres  # Password to access the database
        N_TABLE_ROWS: 5              # Number of rows present in each table initially
        INSERT_RATE: 1               # Number of rows to insert/add per second
        UPDATE_RATE: 1               #                    update
        DELETE_RATE: 0               #                    delete 
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 30s
      retries: 5
```
