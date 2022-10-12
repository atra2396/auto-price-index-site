FROM node:slim AS assets
WORKDIR /app
COPY package.json package-lock.json ./
COPY static/styles.css .
RUN npm ci && npx tailwindcss -i ./styles.css -o main.css

FROM python:3.9-slim
WORKDIR /app
COPY --from=assets /app/main.css /app/main.css
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT gunicorn --worker-tmp-dir /dev/shm -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0 main:app