
## Initial Setup
```sh
touch Dockerfile docker-compose.yml requirements.txt requirements-dev.txt .dockerignore .env README.md

mkdir -p app/api/routers app/core tests/api

touch app/api/routers/health.py
touch app/core/config.py app/core/logging.py

touch app/main.py

touch tests/__init__.py
touch tests/api/test_health.py

```

Build the image & test:
```sh

docker compose build --no-cache

docker compose up --build

docker compose run --rm api pytest

curl http://localhost:8000/health

```

## Alembic

```sh
docker compose down -v
docker compose build api

docker compose run --rm api alembic init alembic

```

Edit `alembic/env.py` before proceeding:
```py
# from app.db import Base
# from app import models
from app.db.base import Base
from app.db.models import *  # noqa: F401, F403

target_metadata = Base.metadata

database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

```

NOTE: in `alembic.ini`, `sqlalchemy.url = driver://user:pass@localhost/dbname` is just a fallback.
We're already overriding it dynamically in `env.py`.

### Generate & apply first migration
```sh
docker compose run --rm api alembic revision --autogenerate -m "create users and files tables"

docker compose run --rm api alembic upgrade head
```
## files

```sh
docker compose run --rm api alembic revision --autogenerate -m "align files model for storage metadata"
docker compose run --rm api alembic upgrade head
```

## DDX

```sh
docker compose exec db psql -h localhost -U admino -d pixel_caption_db

```
