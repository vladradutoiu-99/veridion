FROM python:3.10-slim

WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT celery --app=app.app worker --pool=prefork --prefetch-multiplier=1 --concurrency=1 --max-tasks-per-child=1 --loglevel=info 