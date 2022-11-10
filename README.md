# Satellite

This repository contains a `Dockerfile` suitable to build a postgres instance
that mimics the table structure of
[EMAP star](https://github.com/inform-health-informatics/Inform-DB) populated
with fake data.

Run as a single container:
```bash
docker build . -t satellite
docker run -p 5432:5432 satellite
```

Use in a Docker compose file:
```yaml
version: "3.9"

services:
  star:
    image: satellite
    container_name: test_fake_star_db
    build:
      context: .
      dockerfile: Dockerfile
      args:
        POSTGRES_USER: postgres      # Username to access the database
        POSTGRES_PASSWORD: postgres  # Password to access the database
        N_TABLE_ROWS: 5              # Number of rows present in each table
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 30s
      retries: 5
```
