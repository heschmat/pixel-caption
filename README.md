

```sh
touch Dockerfile docker-compose.yml requirements.txt requirements-dev.txt .dockerignore .env README.md

mkdir -p app/api/routers app/core tests/api

touch app/api/routers/health.py
touch app/core/config.py app/core/logging.py

touch app/main.py

touch tests/__init__.py
touch tests/api/test_health.py

```