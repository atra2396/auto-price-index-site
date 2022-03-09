FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0 main:app