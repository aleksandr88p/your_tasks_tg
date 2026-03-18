"""
Базовые обработчики команд: /start, /help
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

📋 <b>Основные команды:</b>
/start - это сообщение
/help - справка по командам
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

@router.message(F.text)
async def echo_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer("Я не понимаю эту команду. Используйте /help для списка команд.")
