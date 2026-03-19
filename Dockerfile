# 1. Базовый образ - Python 3.12 легкая версия
FROM python:3.12-slim

# 2. Рабочая директория внутри контейнера
WORKDIR /app

# 3. Копируем .env файл
COPY .env .

# 4. Копируем только зависимости сначала (кэширование)
COPY requirements.txt .

# 5. Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копируем код приложения
COPY bot/ ./bot/
COPY config/ ./config/
COPY main.py .

# 7. Команда запуска приложения (порт не нужен, бот не слушает порт)
CMD ["python", "-m", "bot.main"]
