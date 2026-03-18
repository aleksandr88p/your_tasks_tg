"""
Точка входа в Telegram-бота YourTasks
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import settings
from bot.handlers.base import router as base_router
from bot.handlers.tasks import router as tasks_router
from bot.handlers.time import router as time_router

# Настройка логирования
logging.basicConfig(level=settings.LOG_LEVEL, stream=sys.stdout)
logger = logging.getLogger(__name__)

async def set_bot_commands(bot: Bot):
    """Установить команды бота для автодополнения"""
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота и показать меню"),
        BotCommand(command="new", description="📝 Создать новую задачу"),
        BotCommand(command="list", description="📋 Показать все задачи"),
        BotCommand(command="time", description="⏰ Добавить время к задаче"),
        BotCommand(command="complete", description="✅ Завершить задачу"),
        BotCommand(command="active", description="🟢 Активировать задачу"),
        BotCommand(command="stats", description="📊 Показать статистику"),
        BotCommand(command="help", description="❓ Показать справку")
    ]
    
    await bot.set_my_commands(commands)
    logger.info("📋 Команды бота установлены")

async def main():
    """Главная функция запуска бота"""
    try:
        # Создаем экземпляр бота
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Создаем диспетчер с FSM хранилищем
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Устанавливаем команды бота
        await set_bot_commands(bot)
        
        logger.info("🤖 YourTasks Bot запускается...")
        logger.info(f"🔗 API URL: {settings.API_URL}")
        
        # Подключаем роутеры
        dp.include_router(base_router)
        dp.include_router(tasks_router)
        dp.include_router(time_router)
        
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
