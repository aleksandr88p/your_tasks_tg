"""
Базовые обработчики команд: /start, /help, /lang
"""
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

from config.settings import settings
from bot.utils.user_storage import set_user_language, get_user_language

# Создаем роутер
router = Router()

@router.message(CommandStart())
async def handle_start(message: types.Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name or message.from_user.username or "пользователь"
    lang = get_user_language(message.from_user.id)
    
    if lang == "en":
        text = f"""
👋 Hello, {user_name}!

I'm <b>YourTasks Bot</b>, your task management assistant!

🚀 <b>What I can do:</b>
• Create tasks
• Log time
• Show statistics
• Work in two languages

📋 <b>Basic commands:</b>
/start - this message
/help - command help
/lang - change language (RU/EN)
/new &lt;title&gt; - create task
/list - show all tasks
/time &lt;id&gt; &lt;minutes&gt; - add time (in minutes)
/stats - statistics

💡 <b>Usage examples:</b>
/new Learn Spanish language
/time 1 45 Studied with textbook
/list

Let's start! Create your first task with /new command
"""
    else:
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
/new &lt;название&gt; - создать задачу
/list - показать все задачи
/time &lt;id&gt; &lt;минуты&gt; - добавить время (в минутах)
/stats - статистика

💡 <b>Примеры использования:</b>
/new Изучить испанский язык
/time 1 45 Занимался по учебнику
/list

Давай начнем! Создай свою первую задачу командой /new
"""
    
    await message.answer(text)

@router.message(Command("help"))
async def handle_help(message: types.Message):
    """Обработчик команды /help"""
    lang = get_user_language(message.from_user.id)
    
    if lang == "en":
        text = """
📚 <b>YourTasks Bot Command Help</b>

🔧 <b>Task Management:</b>
/new &lt;title&gt; - create new task
/list - show all tasks
/task &lt;id&gt; - task details
/complete &lt;id&gt; - mark as completed
/active &lt;id&gt; - activate task

⏰ <b>Time Tracking:</b>
/time &lt;id&gt; &lt;minutes&gt; [comment] - add time in minutes
/log - all time logs
/stats - general statistics
/task_stats &lt;id&gt; - task statistics

⚙️ <b>Settings:</b>
/lang - change language (RU/EN)
/help - this help
/start - greeting

💡 <b>Examples:</b>
/new Apartment cleaning
/time 1 30 Washed dishes
/stats

❓ <b>Need help?</b>
Use /start to begin!
"""
    else:
        text = """
📚 <b>Справка по командам YourTasks Bot</b>

🔧 <b>Управление задачами:</b>
/new &lt;название&gt; - создать новую задачу
/list - показать все задачи
/task &lt;id&gt; - детали задачи
/complete &lt;id&gt; - отметить выполненной
/active &lt;id&gt; - активировать задачу

⏰ <b>Работа со временем:</b>
/time &lt;id&gt; &lt;минуты&gt; [комментарий] - добавить время в минутах
/log - все логи времени
/stats - общая статистика
/task_stats &lt;id&gt; - статистика по задаче

⚙️ <b>Настройки:</b>
/lang - смена языка (RU/EN)
/help - эта справка
/start - приветствие

💡 <b>Примеры:</b>
/new Уборка квартиры
/time 1 30 Мыли посуду
/stats

❓ <b>Нужна помощь?</b>
Используй /start для начала работы!
"""
    
    await message.answer(text)

@router.message(Command("lang"))
async def handle_lang(message: types.Message):
    """Обработчик команды /lang"""
    lang = get_user_language(message.from_user.id)
    
    if lang == "en":
        text = """
🌐 <b>Choose language / Выберите язык:</b>

🇷🇺 Русский - /lang_ru
🇬🇧 English - /lang_en

💡 Language will be saved for all future messages!
"""
    else:
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
    set_user_language(message.from_user.id, "ru")
    await message.answer("🇷🇺 Язык изменен на русский")

@router.message(Command("lang_en"))
async def handle_lang_en(message: types.Message):
    """Установить английский язык"""
    set_user_language(message.from_user.id, "en")
    await message.answer("🇬🇧 Language changed to English")
