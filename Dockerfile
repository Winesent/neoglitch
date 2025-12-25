# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем зависимости и обновляем пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости первыми (для кэширования слоя)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Создаём файл data.db (чтобы SQLite имел права на запись)
RUN touch data.db

# Экспонируем порт 8000
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]