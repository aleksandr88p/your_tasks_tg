FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY bot/ ./bot/
COPY config/ ./config/
COPY main.py .

# Запускаем бота
CMD ["python", "-m", "bot.main"]
