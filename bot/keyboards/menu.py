"""
Клавиатуры для Telegram бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="📝 Новая задача"),
        KeyboardButton(text="🟢 Активные задачи")
    )
    builder.row(
        KeyboardButton(text="✅ Завершенные задачи"),
        KeyboardButton(text="📋 Все задачи")
    )
    builder.row(
        KeyboardButton(text="⏰ Добавить время"),
        KeyboardButton(text="📅 Время за другой день")
    )
    builder.row(
        KeyboardButton(text="🗑️ Waste Time"),
        KeyboardButton(text="📊 Статистика Waste Time")
    )
    builder.row(
        KeyboardButton(text="📊 Статистика"),
        KeyboardButton(text="🏁 Завершить задачу")
    )
    builder.row(
        KeyboardButton(text="🔄 Активировать задачу"),
        KeyboardButton(text="❌ Отмена")
    )
    builder.row(
        KeyboardButton(text="❓ Помощь")
    )
    
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_task_actions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для действий с задачей"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⏰ Добавить время", callback_data="add_time"),
        InlineKeyboardButton(text="✅ Завершить", callback_data="complete_task")
    )
    builder.row(
        InlineKeyboardButton(text="🟢 Активировать", callback_data="activate_task"),
        InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_task")
    )
    
    return builder.as_markup()

def get_tasks_list_keyboard(tasks: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком задач для выбора"""
    builder = InlineKeyboardBuilder()
    
    for i, task in enumerate(tasks, 1):
        status_emoji = "🟢" if task.get('status') == 'active' else "✅"
        title = task.get('title', 'Без названия')
        task_id = task.get('id')
        
        builder.row(
            InlineKeyboardButton(
                text=f"{i}. {status_emoji} {title}",
                callback_data=f"select_task_{task_id}"
            )
        )
    
    return builder.as_markup()

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(KeyboardButton(text="❌ Отмена"))
    
    return builder.as_markup(resize_keyboard=True)

def get_back_to_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для возврата в главное меню"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(KeyboardButton(text="🏠 Главное меню"))
    
    return builder.as_markup(resize_keyboard=True)
