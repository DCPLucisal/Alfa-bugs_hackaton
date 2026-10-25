FROM python:3.11-slim

WORKDIR /app


COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock

# Копируем весь код
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем FastAPI
CMD ["sh", "-c", "sleep 5 && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]