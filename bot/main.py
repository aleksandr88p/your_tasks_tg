"""
Точка входа в Telegram-бота YourTasks
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import settings
from bot.handlers.base import router as base_router

# Настройка логирования
logging.basicConfig(level=settings.LOG_LEVEL, stream=sys.stdout)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    try:
        # Создаем экземпляр бота
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Создаем диспетчер
        dp = Dispatcher()
        
        logger.info("🤖 YourTasks Bot запускается...")
        logger.info(f"🔗 API URL: {settings.API_URL}")
        logger.info(f"🌐 Язык по умолчанию: {settings.DEFAULT_LANGUAGE}")
        
        # Подключаем роутеры
        dp.include_router(base_router)
        
        # Запускаем бота в режиме polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
