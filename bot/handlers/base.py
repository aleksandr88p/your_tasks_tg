"""
Базовые обработчики команд: /start, /help, /lang
"""
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

from config.settings import settings

# Создаем роутер
router = Router()

@router.message(CommandStart())
async def handle_start(message: types.Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name or message.from_user.username or "пользователь"
    
    text = f"""
👋 Привет, {user_name}!

Я — <b>YourTasks Bot</b>, твой помощник для управления задачами!

🚀 <b>Что я умею:</b>
• Создавать задачи
• Логировать время
• Показывать статистику
• Работать на двух языках

📋 <b>Основные команды:</b>
/start - это сообщение
/help - справка по командам
/lang - смена языка (RU/EN)
/new <название> - создать задачу
/list - показать все задачи
/time <id> <минуты> - добавить время
/stats - статистика

💡 <b>Примеры использования:</b>
/new Изучить Python
/time 1 45 Читал документацию
/list

Давай начнем! Создай свою первую задачу командой /new
"""
    
    await message.answer(text)

@router.message(Command("help"))
async def handle_help(message: types.Message):
    """Обработчик команды /help"""
    text = """
📚 <b>Справка по командам YourTasks Bot</b>

🔧 <b>Управление задачами:</b>
/new <название> - создать новую задачу
/list - показать все задачи
/task <id> - детали задачи
/complete <id> - отметить выполненной
/active <id> - активировать задачу

⏰ <b>Работа со временем:</b>
/time <id> <минуты> [комментарий] - добавить время
/log - все логи времени
/stats - общая статистика
/task_stats <id> - статистика по задаче

⚙️ <b>Настройки:</b>
/lang - смена языка (RU/EN)
/help - эта справка
/start - приветствие

💡 <b>Примеры:</b>
/new Изучить aiogram
/time 1 30 Практика с хендлерами
/stats

❓ <b>Нужна помощь?</b>
Используй /start для начала работы!
"""
    
    await message.answer(text)

@router.message(Command("lang"))
async def handle_lang(message: types.Message):
    """Обработчик команды /lang"""
    text = """
🌐 <b>Выберите язык / Select language:</b>

🇷🇺 Русский - /lang_ru
🇬🇧 English - /lang_en

💡 Язык сохранится для всех будущих сообщений!
"""
    
    await message.answer(text)

@router.message(Command("lang_ru"))
async def handle_lang_ru(message: types.Message):
    """Установить русский язык"""
    # TODO: Здесь будет сохранение языка в БД
    await message.answer("🇷🇺 Язык изменен на русский")

@router.message(Command("lang_en"))
async def handle_lang_en(message: types.Message):
    """Установить английский язык"""
    # TODO: Здесь будет сохранение языка в БД
    await message.answer("🇬🇧 Language changed to English")
