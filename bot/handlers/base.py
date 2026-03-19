"""
Базовые обработчики команд: /start, /help
"""
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

from config.settings import settings
from bot.handlers.tasks import handle_new_task
from bot.services.api_client import api_client
from bot.keyboards import get_main_menu, get_cancel_keyboard, get_back_to_menu_keyboard

# Создаем роутер
router = Router()

# Переменная для отслеживания состояния пользователя
user_states = {}  # {user_id: {'action': 'new_task', 'step': 1}}

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

📋 <b>Используй кнопки ниже для быстрого доступа:</b>
"""
    
    await message.answer(text, reply_markup=get_main_menu())

@router.message(Command("help"))
async def handle_help(message: types.Message):
    """Обработчик команды /help"""
    text = """
📚 <b>Справка по командам YourTasks Bot</b>

🔧 <b>Основные команды:</b>
/start - Показать главное меню
/help - Эта справка

📋 <b>Управление задачами:</b>
/new - Создать новую задачу
/list - Показать все задачи
/complete - Завершить задачу
/active - Активировать задачу

⏰ <b>Работа со временем:</b>
/time - Добавить время к задаче
/stats - Общая статистика

🎮 <b>Кнопки (рекомендуется):</b>
📝 Новая задача - создать задачу
🟢 Активные задачи - показать только активные
✅ Завершенные задачи - показать только завершенные
📋 Все задачи - показать все задачи
⏰ Добавить время - логировать время
� Статистика - посмотреть статистику
❌ Отмена - отменить текущее действие

💡 <b>Совет:</b> Используй кнопки для удобства или набери / чтобы увидеть все команды!
"""
    
    await message.answer(text, reply_markup=get_main_menu())

@router.message(F.text)
async def debug_all_messages(message: types.Message):
    """Обработчик всех сообщений"""
    
    # Обработка кнопок главного меню
    if message.text == "📝 Новая задача":
        # Устанавливаем состояние ожидания названия задачи
        user_states[message.from_user.id] = {'action': 'new_task', 'step': 'waiting_title'}
        await message.answer(
            "📝 Введите название задачи:\n\n"
            "Пример: Изучить Python\n"
            "Пример: Убрать комнату\n"
            "Пример: Прочитать книгу",
            reply_markup=get_cancel_keyboard()
        )
    elif message.text == "🟢 Активные задачи":
        await handle_active_tasks(message)
    elif message.text == "✅ Завершенные задачи":
        await handle_completed_tasks(message)
    elif message.text == "📋 Все задачи":
        await handle_list_tasks(message)
    elif message.text == "⏰ Добавить время":
        # Показываем список задач и просим выбрать по порядку
        try:
            tasks = await api_client.get_tasks(message.from_user.id)
            
            if not tasks:
                await message.answer("📝 У вас пока нет задач. Создайте первую командой 📝 Новая задача")
                return
            
            # Формируем список задач с порядковыми номерами
            response_text = "⏰ <b>Выберите задачу по порядковому номеру:</b>\n\n"
            for i, task in enumerate(tasks, 1):
                status_emoji = "🟢" if task.get('status') == 'active' else "✅"
                response_text += f"{i}. {status_emoji} {task.get('title')} (ID: {task.get('id')})\n"
            
            response_text += "\nВведите номер задачи (1, 2, 3...):"
            
            # Сохраняем список задач для выбора
            user_states[message.from_user.id] = {
                'action': 'add_time', 
                'step': 'waiting_task_number', 
                'tasks': tasks
            }
            
            await message.answer(response_text, reply_markup=get_cancel_keyboard())
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении задач: {str(e)}")
    elif message.text == "🏁 Завершить задачу":
        # Показываем список задач и просим выбрать по порядку
        try:
            tasks = await api_client.get_tasks(message.from_user.id)
            
            if not tasks:
                await message.answer("📝 У вас пока нет задач")
                return
            
            # Формируем список задач с порядковыми номерами
            response_text = "🏁 <b>Выберите задачу для завершения по номеру:</b>\n\n"
            for i, task in enumerate(tasks, 1):
                status_emoji = "🟢" if task.get('status') == 'active' else "✅"
                response_text += f"{i}. {status_emoji} {task.get('title')} (ID: {task.get('id')})\n"
            
            response_text += "\nВведите номер задачи (1, 2, 3...):"
            
            # Сохраняем список задач для выбора
            user_states[message.from_user.id] = {
                'action': 'complete_task', 
                'step': 'waiting_task_number', 
                'tasks': tasks
            }
            
            await message.answer(response_text, reply_markup=get_cancel_keyboard())
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении задач: {str(e)}")
    elif message.text == "� Активировать задачу":
        # Показываем список задач и просим выбрать по порядку
        try:
            tasks = await api_client.get_tasks(message.from_user.id)
            
            if not tasks:
                await message.answer("📝 У вас пока нет задач")
                return
            
            # Формируем список задач с порядковыми номерами
            response_text = "� <b>Выберите задачу для активации по номеру:</b>\n\n"
            for i, task in enumerate(tasks, 1):
                status_emoji = "🟢" if task.get('status') == 'active' else "✅"
                response_text += f"{i}. {status_emoji} {task.get('title')} (ID: {task.get('id')})\n"
            
            response_text += "\nВведите номер задачи (1, 2, 3...):"
            
            # Сохраняем список задач для выбора
            user_states[message.from_user.id] = {
                'action': 'activate_task', 
                'step': 'waiting_task_number', 
                'tasks': tasks
            }
            
            await message.answer(response_text, reply_markup=get_cancel_keyboard())
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении задач: {str(e)}")
    elif message.text == "❌ Отмена":
        # Отменяем текущее действие
        user_id = message.from_user.id
        if user_id in user_states:
            del user_states[user_id]
        
        await message.answer(
            "❌ Действие отменено",
            reply_markup=get_main_menu()
        )
    elif message.text == "🏠 Главное меню":
        await message.answer(
            "🏠 Возврат в главное меню",
            reply_markup=get_main_menu()
        )
    elif message.text == "📊 Статистика":
        await handle_stats_command(message)
    elif message.text == "❓ Помощь":
        await handle_help(message)
    # Обработка старых команд для совместимости
    elif message.text == "/start":
        await handle_start(message)
    elif message.text == "/new":
        # Устанавливаем состояние ожидания названия задачи
        user_states[message.from_user.id] = {'action': 'new_task', 'step': 'waiting_title'}
        await message.answer(
            "📝 Введите название задачи:\n\n"
            "Пример: Изучить Python\n"
            "Пример: Убрать комнату\n"
            "Пример: Прочитать книгу",
            reply_markup=get_cancel_keyboard()
        )
    elif message.text == "/list":
        await handle_list_tasks(message)
    elif message.text == "/time":
        # Показываем список задач и просим выбрать по порядку
        try:
            tasks = await api_client.get_tasks(message.from_user.id)
            
            if not tasks:
                await message.answer("📝 У вас пока нет задач. Создайте первую командой /new")
                return
            
            # Формируем список задач с порядковыми номерами
            response_text = "⏰ <b>Выберите задачу по порядковому номеру:</b>\n\n"
            for i, task in enumerate(tasks, 1):
                status_emoji = "🟢" if task.get('status') == 'active' else "✅"
                response_text += f"{i}. {status_emoji} {task.get('title')} (ID: {task.get('id')})\n"
            
            response_text += "\nВведите номер задачи (1, 2, 3...):"
            
            # Сохраняем список задач для выбора
            user_states[message.from_user.id] = {
                'action': 'add_time', 
                'step': 'waiting_task_number', 
                'tasks': tasks
            }
            
            await message.answer(response_text)
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении задач: {str(e)}")
    elif message.text.startswith("/stats"):
        await handle_stats_command(message)
    elif message.text == "/complete":
        # Показываем список задач и просим выбрать по порядку
        try:
            tasks = await api_client.get_tasks(message.from_user.id)
            
            if not tasks:
                await message.answer("📝 У вас пока нет задач")
                return
            
            # Формируем список задач с порядковыми номерами
            response_text = "✅ <b>Выберите задачу для завершения по номеру:</b>\n\n"
            for i, task in enumerate(tasks, 1):
                status_emoji = "🟢" if task.get('status') == 'active' else "✅"
                response_text += f"{i}. {status_emoji} {task.get('title')} (ID: {task.get('id')})\n"
            
            response_text += "\nВведите номер задачи (1, 2, 3...):"
            
            # Сохраняем список задач для выбора
            user_states[message.from_user.id] = {
                'action': 'complete_task', 
                'step': 'waiting_task_number', 
                'tasks': tasks
            }
            
            await message.answer(response_text)
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении задач: {str(e)}")
    elif message.text == "/active":
        # Показываем список задач и просим выбрать по порядку
        try:
            tasks = await api_client.get_tasks(message.from_user.id)
            
            if not tasks:
                await message.answer("📝 У вас пока нет задач")
                return
            
            # Формируем список задач с порядковыми номерами
            response_text = "🟢 <b>Выберите задачу для активации по номеру:</b>\n\n"
            for i, task in enumerate(tasks, 1):
                status_emoji = "🟢" if task.get('status') == 'active' else "✅"
                response_text += f"{i}. {status_emoji} {task.get('title')} (ID: {task.get('id')})\n"
            
            response_text += "\nВведите номер задачи (1, 2, 3...):"
            
            # Сохраняем список задач для выбора
            user_states[message.from_user.id] = {
                'action': 'activate_task', 
                'step': 'waiting_task_number', 
                'tasks': tasks
            }
            
            await message.answer(response_text)
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении задач: {str(e)}")
    elif message.text.startswith("/"):
        await message.answer("Я не понимаю эту команду. Используйте /help для списка команд.")
    else:
        # Обрабатываем текст только если есть состояние
        user_id = message.from_user.id
        if user_id in user_states:
            state = user_states[user_id]
            await handle_user_input(message, state)
        else:
            # Если нет состояния - просто подсказка
            await message.answer("Я не понимаю. Используйте /help для списка команд.")

async def handle_user_input(message: types.Message, state: dict):
    """Обработать ввод пользователя в зависимости от состояния"""
    user_id = message.from_user.id
    action = state['action']
    step = state['step']
    
    if action == 'new_task' and step == 'waiting_title':
        # Создаем задачу
        await create_task_from_text(message, message.text)
        # Сбрасываем состояние
        del user_states[user_id]
        
    elif action == 'add_time' and step == 'waiting_task_number':
        try:
            task_number = int(message.text)
            tasks = state['tasks']
            
            if task_number < 1 or task_number > len(tasks):
                await message.answer(f"❌ Введите число от 1 до {len(tasks)}")
                return
                
            # Получаем задачу по номеру
            selected_task = tasks[task_number - 1]
            task_id = selected_task.get('id')
            
            # Сохраняем ID и переходим к следующему шагу
            user_states[user_id] = {
                'action': 'add_time', 
                'step': 'waiting_minutes', 
                'task_id': task_id,
                'task_title': selected_task.get('title')
            }
            await message.answer(
                f"⏰ Введите количество минут для задачи «{selected_task.get('title')}»:\n\n"
                "Пример: 30\n"
                "Пример: 45"
            )
        except ValueError:
            await message.answer("❌ Введите число - номер задачи")
            
    elif action == 'add_time' and step == 'waiting_minutes':
        try:
            minutes = int(message.text)
            if minutes <= 0:
                await message.answer("❌ Количество минут должно быть положительным числом")
                return
                
            # Сохраняем минуты и переходим к комментарию
            user_states[user_id] = {
                'action': 'add_time', 
                'step': 'waiting_comment', 
                'task_id': state['task_id'], 
                'minutes': minutes,
                'task_title': state.get('task_title')
            }
            await message.answer(
                f"⏰ Введите комментарий (обязательно):\n\n"
                "Пример: Практика с Python\n"
                "Пример: Читал документацию\n"
                "Пример: Решал задачи"
            )
        except ValueError:
            await message.answer("❌ Введите число - количество минут")
            
    elif action == 'add_time' and step == 'waiting_comment':
        # Добавляем время
        comment = message.text.strip()
        if not comment:
            await message.answer("❌ Комментарий обязателен. Введите описание:")
            return
            
        try:
            result = await api_client.add_time(
                user_id, 
                state['task_id'], 
                state['minutes'], 
                comment
            )
            
            await message.answer(
                f"⏰ Время добавлено!\n\n"
                f"📋 Задача: {state.get('task_title', 'N/A')}\n"
                f"⏱️ Минут: {state['minutes']}\n"
                f"💬 Комментарий: {comment}\n"
                f"🕐 Лог ID: {result.get('id', 'N/A')}\n\n"
                f"Что делаем дальше?",
                reply_markup=get_main_menu()
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка при добавлении времени: {str(e)}")
        
        # Сбрасываем состояние
        del user_states[user_id]
        
    elif action == 'complete_task' and step == 'waiting_task_number':
        try:
            task_number = int(message.text)
            tasks = state['tasks']
            
            if task_number < 1 or task_number > len(tasks):
                await message.answer(f"❌ Введите число от 1 до {len(tasks)}")
                return
                
            # Получаем задачу по номеру
            selected_task = tasks[task_number - 1]
            task_id = selected_task.get('id')
            
            try:
                result = await api_client.update_task_status(user_id, task_id, "completed")
                await message.answer(
                    f"✅ Задача отмечена как выполненная!\n\n"
                    f"📋 {selected_task.get('title')}\n"
                    f"🆔 ID: {task_id}\n\n"
                    f"Что делаем дальше?",
                    reply_markup=get_main_menu()
                )
            except Exception as e:
                await message.answer(f"❌ Ошибка при завершении задачи: {str(e)}")
            
            # Сбрасываем состояние
            del user_states[user_id]
            
        except ValueError:
            await message.answer("❌ Введите число - номер задачи")
            
    elif action == 'activate_task' and step == 'waiting_task_number':
        try:
            task_number = int(message.text)
            tasks = state['tasks']
            
            if task_number < 1 or task_number > len(tasks):
                await message.answer(f"❌ Введите число от 1 до {len(tasks)}")
                return
                
            # Получаем задачу по номеру
            selected_task = tasks[task_number - 1]
            task_id = selected_task.get('id')
            
            try:
                result = await api_client.update_task_status(user_id, task_id, "active")
                await message.answer(
                    f"🟢 Задача активирована!\n\n"
                    f"📋 {selected_task.get('title')}\n"
                    f"🆔 ID: {task_id}\n\n"
                    f"Что делаем дальше?",
                    reply_markup=get_main_menu()
                )
            except Exception as e:
                await message.answer(f"❌ Ошибка при активации задачи: {str(e)}")
            
            # Сбрасываем состояние
            del user_states[user_id]
            
        except ValueError:
            await message.answer("❌ Введите число - номер задачи")

async def create_task_from_text(message: types.Message, task_title: str):
    """Создать задачу из текста пользователя"""
    
    try:
        # Создаем задачу через API
        result = await api_client.create_task(message.from_user.id, task_title.strip())
        
        await message.answer(
            f"✅ Задача создана!\n\n"
            f"📋 Название: {result.get('title', task_title)}\n"
            f"🆔 ID: {result.get('id', 'N/A')}\n"
            f"📅 Статус: {result.get('status', 'active')}\n\n"
            f"Хотите добавить время к этой задаче?",
            reply_markup=get_back_to_menu_keyboard()
        )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании задачи: {str(e)}")

async def handle_active_tasks(message: types.Message):
    """Обработчик для показа только активных задач"""
    try:
        tasks = await api_client.get_tasks(message.from_user.id)
        print(f"[DEBUG] Все задачи: {tasks}")  # Отладка
        
        # Фильтруем только активные задачи
        active_tasks = [task for task in tasks if task.get('status') == 'active']
        print(f"[DEBUG] Активные задачи: {active_tasks}")  # Отладка
        print(f"[DEBUG] Количество активных: {len(active_tasks)}")  # Отладка
        
        if not active_tasks:
            await message.answer("🟢 У вас нет активных задач. Создайте новую командой 📝 Новая задача", reply_markup=get_main_menu())
            return
        
        response_text = f"🟢 <b>Активные задачи ({len(active_tasks)}):</b>\n\n"
        for task in active_tasks:
            # Получаем время для задачи
            task_time = await api_client.get_task_time(message.from_user.id, task.get('id'))
            hours = task_time // 60
            minutes = task_time % 60
            
            time_text = ""
            if task_time > 0:
                if hours > 0:
                    time_text = f"⏱️ {hours}ч {minutes}м"
                else:
                    time_text = f"⏱️ {minutes}м"
            else:
                time_text = "⏱️ 0м"
            
            response_text += (
                f"🟢 <b>ID: {task.get('id')}</b> - {task.get('title')}\n"
                f"   {time_text} | Статус: {task.get('status', 'unknown')}\n\n"
            )
        
        print(f"[DEBUG] Ответ для активных: {response_text}")  # Отладка
        await message.answer(response_text, reply_markup=get_main_menu())
        
    except Exception as e:
        print(f"[DEBUG] Ошибка: {e}")  # Отладка
        await message.answer(f"❌ Ошибка при получении активных задач: {str(e)}", reply_markup=get_main_menu())

async def handle_completed_tasks(message: types.Message):
    """Обработчик для показа только завершенных задач"""
    try:
        tasks = await api_client.get_tasks(message.from_user.id)
        
        # Фильтруем только завершенные задачи
        completed_tasks = [task for task in tasks if task.get('status') == 'completed']
        
        if not completed_tasks:
            await message.answer("✅ У вас нет завершенных задач. Создайте новую командой 📝 Новая задача", reply_markup=get_main_menu())
            return
        
        response_text = f"✅ <b>Завершенные задачи ({len(completed_tasks)}):</b>\n\n"
        for task in completed_tasks:
            # Получаем время для задачи
            task_time = await api_client.get_task_time(message.from_user.id, task.get('id'))
            hours = task_time // 60
            minutes = task_time % 60
            
            time_text = ""
            if task_time > 0:
                if hours > 0:
                    time_text = f"⏱️ {hours}ч {minutes}м"
                else:
                    time_text = f"⏱️ {minutes}м"
            else:
                time_text = "⏱️ 0м"
            
            response_text += (
                f"✅ <b>ID: {task.get('id')}</b> - {task.get('title')}\n"
                f"   {time_text} | Статус: {task.get('status', 'unknown')}\n\n"
            )
        
        await message.answer(response_text, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении завершенных задач: {str(e)}", reply_markup=get_main_menu())

async def handle_list_tasks(message: types.Message):
    """Обработчик команды /list"""
    try:
        tasks = await api_client.get_tasks(message.from_user.id)
        
        if not tasks:
            await message.answer("📝 У вас пока нет задач. Создайте первую командой /new")
            return
        
        response_text = "📋 <b>Ваши задачи:</b>\n\n"
        for task in tasks:
            status_emoji = "🟢" if task.get('status') == 'active' else "✅"
            
            # Получаем время для задачи
            task_time = await api_client.get_task_time(message.from_user.id, task.get('id'))
            hours = task_time // 60
            minutes = task_time % 60
            
            time_text = ""
            if task_time > 0:
                if hours > 0:
                    time_text = f"⏱️ {hours}ч {minutes}м"
                else:
                    time_text = f"⏱️ {minutes}м"
            else:
                time_text = "⏱️ 0м"
            
            response_text += (
                f"{status_emoji} <b>ID: {task.get('id')}</b> - {task.get('title')}\n"
                f"   {time_text} | Статус: {task.get('status', 'unknown')}\n\n"
            )
        
        await message.answer(response_text)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении задач: {str(e)}")

async def handle_time_command(message: types.Message):
    """Обработчик команды /time"""
    parts = message.text.split()
    
    if len(parts) < 3:
        await message.answer(
            "❌ Неверный формат команды!\n"
            "Пример: /time 1 45 Занимался по учебнику\n"
            "где 1 - ID задачи, 45 - минуты"
        )
        return
    
    try:
        task_id = int(parts[1])
        minutes = int(parts[2].split()[0])
        
        if minutes <= 0:
            await message.answer("❌ Количество минут должно быть положительным числом")
            return
        
        # Извлекаем комментарий
        comment_parts = parts[2].split(maxsplit=1)
        comment = comment_parts[1] if len(comment_parts) > 1 else ""
        
        result = await api_client.add_time(message.from_user.id, task_id, minutes, comment)
        
        await message.answer(
            f"⏰ Время добавлено!\n\n"
            f"📋 Задача ID: {task_id}\n"
            f"⏱️ Минут: {minutes}\n"
            f"💬 Комментарий: {comment or 'Без комментария'}\n"
            f"🕐 Лог ID: {result.get('id', 'N/A')}"
        )
        
    except ValueError:
        await message.answer("❌ ID задачи и минуты должны быть числами")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении времени: {str(e)}")

async def handle_stats_command(message: types.Message):
    """Обработчик команды /stats"""
    try:
        stats = await api_client.get_stats(message.from_user.id)
        print(f"[DEBUG] Статистика: {stats}")  # Отладка
        
        total_minutes = stats.get('total_minutes', 0)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        total_tasks = stats.get('total_tasks', 0)
        active_tasks = stats.get('active_tasks', 0)
        completed_tasks = stats.get('completed_tasks', 0)
        
        response_text = (
            f"📊 <b>Ваша статистика:</b>\n\n"
            f"📋 Всего задач: {total_tasks}\n"
            f"🟢 Активные: {active_tasks}\n"
            f"✅ Завершенные: {completed_tasks}\n"
            f"⏱️ Общее время: {hours}ч {minutes}м ({total_minutes} минут)\n"
        )
        
        await message.answer(response_text, reply_markup=get_main_menu())
        
    except Exception as e:
        print(f"[DEBUG] Ошибка статистики: {e}")  # Отладка
        await message.answer(f"❌ Ошибка при получении статистики: {str(e)}", reply_markup=get_main_menu())

async def handle_complete_command(message: types.Message):
    """Обработчик команды /complete"""
    parts = message.text.split()
    
    if len(parts) < 2:
        await message.answer("❌ Укажите ID задачи\nПример: /complete 1")
        return
    
    try:
        task_id = int(parts[1])
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

async def handle_active_command(message: types.Message):
    """Обработчик команды /active"""
    parts = message.text.split()
    
    if len(parts) < 2:
        await message.answer("❌ Укажите ID задачи\nПример: /active 1")
        return
    
    try:
        task_id = int(parts[1])
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
