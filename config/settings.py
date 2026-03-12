import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings:
    """Класс с настройками проекта"""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # YourTasks API
    API_URL = os.getenv("API_URL", "http://185.182.82.203:8000")
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Язык по умолчанию
    DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ru")
    
    # Поддерживаемые языки
    SUPPORTED_LANGUAGES = ["ru", "en"]
    
    @classmethod
    def validate(cls):
        """Проверка обязательных настроек"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не указан в переменных окружения!")
        
        if cls.BOT_TOKEN == "your_telegram_bot_token_here":
            raise ValueError("Пожалуйста, укажите реальный BOT_TOKEN в файле .env")

# Проверяем настройки при импорте
Settings.validate()

# Глобальный экземпляр настроек
settings = Settings()
