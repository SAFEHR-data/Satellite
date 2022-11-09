# fake-star

This repository contains a `Dockerfile` suitable to build a postgres instance
that mimics the table structure of
[EMAP star](https://github.com/inform-health-informatics/Inform-DB) populated
with fake data.

Run as a single container:
```bash
docker build . -t fake-star --build-arg GITHUB_PASSWORD=<token> --build-arg GITHUB_USER=<username>
docker run -p 5432:5432 fake-star
```

Use in a Docker compose file:
```yaml
version: "3.9"

services:
  star:
    image: fake-star
    container_name: test_fake_star
    build:
      context: .
      dockerfile: Dockerfile
      args:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
        GITHUB_USER: <your-github-username>
        GITHUB_PASSWORD: <a-github-PAT>
        N_TABLE_ROWS: 5  # Number of rows present in each table
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 30s
      retries: 5
```
