FROM python:3.12-slim
WORKDIR /app
COPY backend/app.py ./backend/app.py
COPY frontend ./frontend
ENV PORT=8087
ENV CHECKER_TOKEN=checker-secret
EXPOSE 8087
CMD ["python", "backend/app.py"]
