FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD uvicorn app.app:app --host 0.0.0.0 --port 80 --log-level debug
EXPOSE 80