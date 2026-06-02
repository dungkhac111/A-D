FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends steghide libjpeg-turbo-progs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/app.py ./backend/app.py
COPY frontend ./frontend
ENV PORT=8084
ENV CHECKER_TOKEN=checker-secret
EXPOSE 8084
CMD ["python", "backend/app.py"]
