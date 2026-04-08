FROM python:3.12-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV PYTHONPATH=/code

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

# RUN chmod +x /code/scripts/run.sh
CMD ["./scripts/run.sh"]
