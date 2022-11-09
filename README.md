# fake-star

Use in a Docker compose file like:
```yaml
  star:
    image: fake-star
    container_name: test_fake_star
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 30s
      retries: 5
    build:
      context: .
      dockerfile: Dockerfile
      args:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
        GIT_USER: <your-github-username>
        GIT_PASSWORD: <a-github-PAT>
```
