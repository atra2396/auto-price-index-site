FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT gunicorn --worker-tmp-dir /dev/shm -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0 main:app