"""
Обработчики команд для работы с задачами
"""
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.services.api_client import api_client

# FSM для создания задачи
class CreateTaskState(StatesGroup):
    waiting_for_title = State()

# Создаем роутер
router = Router()

@router.message(Command("new"))
async def handle_new_task(message: types.Message):
    """Обработчик команды /new - запрашивает название задачи"""
    print(f"[DEBUG] Получена команда /new от пользователя {message.from_user.id}")
    await message.answer(
        "📝 Введите название задачи:\n\n"
        "Пример: Изучить Python\n"
        "Пример: Убрать комнату\n"
        "Пример: Прочитать книгу",
        parse_mode="HTML"
    )
    print(f"[DEBUG] Отправлен запрос на ввод названия задачи")

@router.message(CreateTaskState.waiting_for_title)
async def process_task_title(message: types.Message, state: FSMContext):
    """Обработчик ввода названия задачи"""
    task_title = message.text.strip()
    
    if not task_title:
        await message.answer("❌ Название задачи не может быть пустым. Попробуйте еще раз:")
        return
    
    try:
        # Создаем задачу через API
        result = await api_client.create_task(message.from_user.id, task_title)
        
        await message.answer(
            f"✅ Задача создана!\n\n"
            f"📋 Название: {result.get('title', task_title)}\n"
            f"🆔 ID: {result.get('id', 'N/A')}\n"
            f"📅 Статус: {result.get('status', 'active')}"
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании задачи: {str(e)}")
    
    # Сбрасываем состояние
    await state.clear()

@router.message(Command("list"))
async def handle_list_tasks(message: types.Message):
    """Обработчик команды /list"""
    try:
        # Получаем задачи через API
        tasks = await api_client.get_tasks(message.from_user.id)
        
        if not tasks:
            await message.answer("📝 У вас пока нет задач. Создайте первую командой /new")
            return
        
        # Формируем список задач
        response_text = "📋 <b>Ваши задачи:</b>\n\n"
        
        for task in tasks:
            status_emoji = "🟢" if task.get('status') == 'active' else "✅"
            response_text += (
                f"{status_emoji} <b>ID: {task.get('id')}</b> - {task.get('title')}\n"
                f"   Статус: {task.get('status', 'unknown')}\n\n"
            )
        
        await message.answer(response_text)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении задач: {str(e)}")

@router.message(Command("task"))
async def handle_task_details(message: types.Message):
    """Обработчик команды /task"""
    parts = message.text.split()
    
    if len(parts) < 2:
        await message.answer("❌ Укажите ID задачи\nПример: /task 1")
        return
    
    try:
        task_id = int(parts[1])
        
        # Получаем детали задачи через API
        task = await api_client.get_task(message.from_user.id, task_id)
        
        response_text = (
            f"📋 <b>Детали задачи:</b>\n\n"
            f"🆔 ID: {task.get('id')}\n"
            f"📝 Название: {task.get('title')}\n"
            f"📅 Статус: {task.get('status')}\n"
            f"🕐 Создана: {task.get('created_at', 'N/A')}"
        )
        
        await message.answer(response_text)
        
    except ValueError:
        await message.answer("❌ ID задачи должен быть числом")
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении задачи: {str(e)}")

@router.message(Command("complete"))
async def handle_complete_task(message: types.Message):
    """Обработчик команды /complete"""
    parts = message.text.split()
    
    if len(parts) < 2:
        await message.answer("❌ Укажите ID задачи\nПример: /complete 1")
        return
    
    try:
        task_id = int(parts[1])
        
        # Обновляем статус задачи через API
        result = await api_client.update_task_status(message.from_user.id, task_id, "completed")
        
        await message.answer(
            f"✅ Задача отмечена как выполненная!\n\n"
            f"📋 {result.get('title')}\n"
            f"🆔 ID: {task_id}"
        )
        
    except ValueError:
        await message.answer("❌ ID задачи должен быть числом")
    except Exception as e:
        await message.answer(f"❌ Ошибка при завершении задачи: {str(e)}")

@router.message(Command("active"))
async def handle_active_task(message: types.Message):
    """Обработчик команды /active"""
    parts = message.text.split()
    
    if len(parts) < 2:
        await message.answer("❌ Укажите ID задачи\nПример: /active 1")
        return
    
    try:
        task_id = int(parts[1])
        
        # Обновляем статус задачи через API
        result = await api_client.update_task_status(message.from_user.id, task_id, "active")
        
        await message.answer(
            f"🟢 Задача активирована!\n\n"
            f"📋 {result.get('title')}\n"
            f"🆔 ID: {task_id}"
        )
        
    except ValueError:
        await message.answer("❌ ID задачи должен быть числом")
    except Exception as e:
        await message.answer(f"❌ Ошибка при активации задачи: {str(e)}")
