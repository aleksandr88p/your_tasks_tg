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
        # Показываем список только активных задач для добавления времени
        try:
            tasks = await api_client.get_tasks(message.from_user.id)
            
            # Фильтруем только активные задачи
            active_tasks = [task for task in tasks if task.get('status') == 'active']
            
            if not active_tasks:
                await message.answer("� У вас нет активных задач для добавления времени", reply_markup=get_main_menu())
                return
            
            # Формируем список активных задач с порядковыми номерами
            response_text = "⏰ <b>Выберите активную задачу для добавления времени:</b>\n\n"
            for i, task in enumerate(active_tasks, 1):
                response_text += f"{i}. 🟢 {task.get('title')} (ID: {task.get('id')})\n"
            
            response_text += "\nВведите номер задачи (1, 2, 3...):"
            
            # Сохраняем список активных задач для выбора
            user_states[message.from_user.id] = {
                'action': 'add_time', 
                'step': 'waiting_task_number', 
                'tasks': active_tasks
            }
            
            await message.answer(response_text, reply_markup=get_cancel_keyboard())
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении задач: {str(e)}", reply_markup=get_main_menu())
    elif message.text == "🏁 Завершить задачу":
        # Показываем список только активных задач для завершения
        try:
            tasks = await api_client.get_tasks(message.from_user.id)
            
            # Фильтруем только активные задачи
            active_tasks = [task for task in tasks if task.get('status') == 'active']
            
            if not active_tasks:
                await message.answer("� У вас нет активных задач для завершения", reply_markup=get_main_menu())
                return
            
            # Формируем список активных задач с порядковыми номерами
            response_text = "🏁 <b>Выберите активную задачу для завершения:</b>\n\n"
            for i, task in enumerate(active_tasks, 1):
                response_text += f"{i}. 🟢 {task.get('title')} (ID: {task.get('id')})\n"
            
            response_text += "\nВведите номер задачи (1, 2, 3...):"
            
            # Сохраняем список активных задач для выбора
            user_states[message.from_user.id] = {
                'action': 'complete_task', 
                'step': 'waiting_task_number', 
                'tasks': active_tasks
            }
            
            await message.answer(response_text, reply_markup=get_cancel_keyboard())
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при получении задач: {str(e)}", reply_markup=get_main_menu())
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
    elif message.text == "📅 Время за другой день":
        # Начинаем процесс добавления времени за другой день
        await handle_add_time_for_past_date(message)
    elif message.text == "🗑️ Waste Time":
        # Начинаем процесс логирования waste time
        await handle_waste_time_start(message)
    elif message.text == "📊 Статистика Waste Time":
        # Показываем статистику waste time
        await handle_waste_time_stats(message)
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

    elif action == 'add_time_past' and step == 'waiting_time_type':
        time_type = message.text.strip()
        
        if time_type == '1':
            # Обычная задача
            try:
                tasks = await api_client.get_tasks(message.from_user.id)
                active_tasks = [task for task in tasks if task.get('status') == 'active']
                
                if not active_tasks:
                    await message.answer("🟢 У вас нет активных задач", reply_markup=get_main_menu())
                    return
                
                response_text = "📅 <b>Выберите активную задачу:</b>\n\n"
                for i, task in enumerate(active_tasks, 1):
                    response_text += f"{i}. 🟢 {task.get('title')} (ID: {task.get('id')})\n"
                response_text += "\nВведите номер задачи (1, 2, 3...):"
                
                user_states[user_id] = {
                    'action': 'add_time_past',
                    'step': 'waiting_task_number',
                    'tasks': active_tasks,
                    'time_type': 'normal'
                }
                await message.answer(response_text, reply_markup=get_cancel_keyboard())
                
            except Exception as e:
                await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=get_main_menu())
                
        elif time_type == '2':
            # Waste Time
            user_states[user_id] = {
                'action': 'add_time_past',
                'step': 'waiting_date',
                'time_type': 'waste'
            }
            await message.answer(
                "📅 <b>Waste Time за другой день</b>\n\n"
                "Введите дату в формате ГГГГ-ММ-ДД:\n\n"
                "Пример: 2026-03-21\n"
                "Пример: 2026-03-20",
                reply_markup=get_cancel_keyboard()
            )
        else:
            await message.answer("❌ Введите 1 или 2")

    elif action == 'add_time_past' and step == 'waiting_task_number':
        try:
            task_number = int(message.text)
            tasks = state['tasks']
            
            if task_number < 1 or task_number > len(tasks):
                await message.answer("❌ Неверный номер задачи. Попробуйте еще раз")
                return
                
            # Получаем задачу по номеру
            selected_task = tasks[task_number - 1]
            task_id = selected_task.get('id')
            
            # Сохраняем задачу и переходим к дате
            user_states[user_id] = {
                'action': 'add_time_past',
                'step': 'waiting_date',
                'task_id': task_id,
                'task_title': selected_task.get('title'),
                'time_type': state.get('time_type', 'normal')
            }
            await message.answer(
                f"📅 Введите дату в формате ГГГГ-ММ-ДД:\n\n"
                f"Пример: 2026-03-21\n"
                f"Пример: 2026-03-20\n\n"
                f"Задача: {selected_task.get('title')}"
            )
        except ValueError:
            await message.answer("❌ Введите число - номер задачи")
            
    elif action == 'add_time_past' and step == 'waiting_date':
        date_text = message.text.strip()
        
        # Простая валидация даты
        try:
            from datetime import datetime
            datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError:
            await message.answer("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        # Сохраняем дату и переходим к минутам
        user_states[user_id] = {
            'action': 'add_time_past',
            'step': 'waiting_minutes',
            'date': date_text,
            'time_type': state.get('time_type', 'normal'),
            'task_id': state.get('task_id'),
            'task_title': state.get('task_title')
        }
        
        if state.get('time_type') == 'waste':
            await message.answer(
                f"🗑️ Введите количество минут потраченных впустую за {date_text}:\n\n"
                f"Пример: 30\n"
                f"Пример: 45"
            )
        else:
            await message.answer(
                f"⏰ Введите количество минут для задачи «{state.get('task_title')}» за {date_text}:\n\n"
                f"Пример: 30\n"
                f"Пример: 45"
            )
        
    elif action == 'add_time_past' and step == 'waiting_minutes':
        try:
            minutes = int(message.text)
            if minutes <= 0:
                await message.answer("❌ Количество минут должно быть положительным числом")
                return
            
            if state.get('time_type') == 'waste':
                # Для waste time сразу переходим к описанию
                user_states[user_id] = {
                    'action': 'add_time_past',
                    'step': 'waiting_waste_description',
                    'date': state['date'],
                    'time_type': 'waste',
                    'minutes': minutes
                }
                await message.answer(
                    f"🗑️ Введите описание что делали {state['date']}:\n\n"
                    f"Пример: Смотрел YouTube\n"
                    f"Пример: Прокрастинировал в соцсетях"
                )
            else:
                # Для обычной задачи переходим к комментарию
                user_states[user_id] = {
                    'action': 'add_time_past',
                    'step': 'waiting_comment',
                    'task_id': state['task_id'],
                    'task_title': state['task_title'],
                    'date': state['date'],
                    'time_type': 'normal',
                    'minutes': minutes
                }
                await message.answer(
                    f"⏰ Введите комментарий для задачи «{state['task_title']}» за {state['date']}:\n\n"
                    f"Пример: Работал над проектом\n"
                    f"Пример: Изучал документацию"
                )
        except ValueError:
            await message.answer("❌ Введите число - количество минут")
            
    elif action == 'add_time_past' and step == 'waiting_waste_description':
        description = message.text.strip()
        
        try:
            # Создаем waste task если нужно
            waste_task_title = "WASTE TIME (непродуктивное время)"
            tasks = await api_client.get_tasks(message.from_user.id)
            waste_task = None
            
            for task in tasks:
                if task.get('title') == waste_task_title:
                    waste_task = task
                    break
            
            if not waste_task:
                waste_task = await api_client.create_task(message.from_user.id, waste_task_title)
            
            # Добавляем время с датой в комментарии
            result = await api_client.add_time(
                message.from_user.id, 
                waste_task.get('id'), 
                state['minutes'], 
                f"WASTE: {description} (дата: {state['date']})"
            )
            
            await message.answer(
                f"🗑️ Waste Time записано!\n\n"
                f"📝 Что делали: {description}\n"
                f"📅 Дата: {state['date']}\n"
                f"⏱️ Минут: {state['minutes']}\n"
                f"🕐 Лог ID: {result.get('id', 'N/A')}\n\n"
                f"Что делаем дальше?",
                reply_markup=get_main_menu()
            )
            
        except Exception as e:
            await message.answer(f"❌ Ошибка при записи waste time: {str(e)}")
        
        del user_states[user_id]
            
    elif action == 'add_time_past' and step == 'waiting_comment':
        comment = message.text.strip()
        
        try:
            # Добавляем время с указанной датой (пока используем текущую дату)
            # TODO: Здесь нужно будет изменить API для поддержки даты
            result = await api_client.add_time(
                message.from_user.id, 
                state['task_id'], 
                state['minutes'], 
                f"{comment} (дата: {state['date']})"
            )
            
            await message.answer(
                f"✅ Время добавлено!\n\n"
                f"📋 Задача: {state['task_title']}\n"
                f"📅 Дата: {state['date']}\n"
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

    elif action == 'waste_time' and step == 'waiting_description':
        description = message.text.strip()
        
        # Сохраняем описание и переходим к минутам
        user_states[user_id] = {
            'action': 'waste_time',
            'step': 'waiting_minutes',
            'description': description
        }
        await message.answer(
            f"🗑️ Введите количество минут потраченного впустую:\n\n"
            f"Пример: 30\n"
            f"Пример: 45"
        )
        
    elif action == 'waste_time' and step == 'waiting_minutes':
        try:
            minutes = int(message.text)
            if minutes <= 0:
                await message.answer("❌ Количество минут должно быть положительным числом")
                return
                
            try:
                # Создаем специальную задачу для waste time или используем существующую
                waste_task_title = "WASTE TIME (непродуктивное время)"
                
                # Ищем существующую waste task
                tasks = await api_client.get_tasks(message.from_user.id)
                waste_task = None
                
                for task in tasks:
                    if task.get('title') == waste_task_title:
                        waste_task = task
                        break
                
                # Если нет waste task, создаем ее
                if not waste_task:
                    waste_task = await api_client.create_task(message.from_user.id, waste_task_title)
                
                # Добавляем время к waste task
                result = await api_client.add_time(
                    message.from_user.id, 
                    waste_task.get('id'), 
                    minutes, 
                    f"WASTE: {state['description']}"
                )
                
                await message.answer(
                    f"🗑️ Waste Time записано!\n\n"
                    f"📝 Что делали: {state['description']}\n"
                    f"⏱️ Минут: {minutes}\n"
                    f"🕐 Лог ID: {result.get('id', 'N/A')}\n\n"
                    f"Что делаем дальше?",
                    reply_markup=get_main_menu()
                )
                
            except Exception as e:
                await message.answer(f"❌ Ошибка при записи waste time: {str(e)}")
            
        except ValueError:
            await message.answer("❌ Введите число - количество минут")
        
        # Сбрасываем состояние
        del user_states[user_id]

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

async def handle_add_time_for_past_date(message: types.Message):
    """Начало процесса добавления времени за другой день"""
    await message.answer(
        "📅 <b>Время за другой день</b>\n\n"
        "Выберите тип времени:\n"
        "1. ⏰ Обычная задача - время для работы\n"
        "2. 🗑️ Waste Time - время впустую\n\n"
        "Введите 1 или 2:",
        reply_markup=get_cancel_keyboard()
    )
    
    # Сохраняем состояние
    user_states[message.from_user.id] = {
        'action': 'add_time_past',
        'step': 'waiting_time_type'
    }

async def handle_waste_time_start(message: types.Message):
    """Начало процесса логирования waste time"""
    await message.answer(
        "🗑️ <b>Waste Time - логирование времени впустую</b>\n\n"
        "Это помогает понять сколько времени тратится не продуктивно.\n\n"
        "Введите описание (что делали):\n"
        "Пример: Смотрел YouTube\n"
        "Пример: Прокрастинировал в соцсетях\n"
        "Пример: Бездельничал",
        reply_markup=get_cancel_keyboard()
    )
    
    # Сохраняем состояние
    user_states[message.from_user.id] = {
        'action': 'waste_time',
        'step': 'waiting_description'
    }

async def handle_waste_time_stats(message: types.Message):
    """Статистика waste time"""
    try:
        # Получаем все задачи
        tasks = await api_client.get_tasks(message.from_user.id)
        
        # Ищем waste task
        waste_task_title = "WASTE TIME (непродуктивное время)"
        waste_task = None
        
        for task in tasks:
            if task.get('title') == waste_task_title:
                waste_task = task
                break
        
        if not waste_task:
            await message.answer("🗑️ У вас пока нет записей о потраченном впустую времени", reply_markup=get_main_menu())
            return
        
        # Получаем все логи времени для waste task
        timelogs = await api_client.get_timelogs(message.from_user.id)
        
        # Фильтруем логи только для waste task
        waste_logs = []
        for log in timelogs:
            if log.get('task_id') == waste_task.get('id'):
                waste_logs.append(log)
        
        if not waste_logs:
            await message.answer("🗑️ У вас пока нет записей о потраченном впустую времени", reply_markup=get_main_menu())
            return
        
        # Считаем статистику
        total_waste_minutes = sum(log.get('minutes', 0) for log in waste_logs)
        today_waste = 0
        last_5_days_waste = 0
        
        from datetime import datetime, timedelta
        now = datetime.now()
        
        for log in waste_logs:
            logged_at = log.get('logged_at', '')
            if logged_at:
                try:
                    log_date = datetime.fromisoformat(logged_at.replace('Z', '+00:00')).date()
                    
                    # За сегодня
                    if log_date == now.date():
                        today_waste += log.get('minutes', 0)
                    
                    # За последние 5 дней
                    if log_date >= (now - timedelta(days=5)).date():
                        last_5_days_waste += log.get('minutes', 0)
                except:
                    continue
        
        # Среднее в день за последние 5 дней
        avg_daily = last_5_days_waste / 5 if last_5_days_waste > 0 else 0
        
        response_text = (
            f"🗑️ <b>Статистика Waste Time:</b>\n\n"
            f"📊 Всего потрачено впустую: {total_waste_minutes // 60}ч {total_waste_minutes % 60}м\n"
            f"📅 Сегодня: {today_waste // 60}ч {today_waste % 60}м\n"
            f"📆 За последние 5 дней: {last_5_days_waste // 60}ч {last_5_days_waste % 60}м\n"
            f"📈 Среднее в день: {avg_daily // 60}ч {avg_daily % 60}м\n\n"
            f"💡 <b>Совет:</b> Попробуйте уменьшить это время на 20% в следующую неделе!"
        )
        
        await message.answer(response_text, reply_markup=get_main_menu())
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статистики: {str(e)}", reply_markup=get_main_menu())
