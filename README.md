# fake-star

Use in a Docker compose file:
```yaml
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
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 30s
      retries: 5
```
