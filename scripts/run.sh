#!/usr/bin/env sh
set -e

echo "⏳ Waiting for database..."

until python -c "from sqlalchemy import create_engine, text; from app.core.config import settings; engine=create_engine(settings.database_url); conn=engine.connect(); conn.execute(text('SELECT 1')); conn.close()"; do
  echo "🔌 Database is unavailable... retrying in 2s"
  sleep 2
done

echo "✅ Database is up!"

echo "📦 Applying database migrations..."
alembic upgrade head
echo "✅ Migrations applied successfully!"

echo "🚀 Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
