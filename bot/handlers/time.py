"""
Обработчики команд для работы со временем
"""
from aiogram import Router, types
from aiogram.filters import Command

from bot.services.api_client import api_client

# Создаем роутер
router = Router()

@router.message(Command("time"))
async def handle_add_time(message: types.Message):
    """Обработчик команды /time"""
    parts = message.text.split(maxsplit=2)
    
    if len(parts) < 3:
        await message.answer(
            "❌ Неверный формат команды!\n"
            "Пример: /time 1 45 Занимался по учебнику\n"
            "где 1 - ID задачи, 45 - минуты"
        )
        return
    
    try:
        task_id = int(parts[1])
        minutes = int(parts[2].split()[0])  # Берем первое число после ID
        
        if minutes <= 0:
            await message.answer("❌ Количество минут должно быть положительным числом")
            return
        
        # Извлекаем комментарий (все что после минут)
        comment_parts = parts[2].split(maxsplit=1)
        comment = comment_parts[1] if len(comment_parts) > 1 else ""
        
        # Добавляем время через API
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

@router.message(Command("log"))
async def handle_time_log(message: types.Message):
    """Обработчик команды /log"""
    try:
        # Получаем все логи времени через API
        timelogs = await api_client.get_timelogs(message.from_user.id)
        
        if not timelogs:
            await message.answer("📝 У вас пока нет записей о времени. Добавьте время командой /time")
            return
        
        # Формируем список логов
        response_text = "📝 <b>Логи времени:</b>\n\n"
        
        for log in timelogs:
            response_text += (
                f"⏰ <b>ID задачи: {log.get('task_id')}</b>\n"
                f"⏱️ Минут: {log.get('minutes')}\n"
                f"💬 {log.get('comment', 'Без комментария')}\n"
                f"🕐 {log.get('logged_at', 'N/A')}\n\n"
            )
        
        await message.answer(response_text)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении логов: {str(e)}")

@router.message(Command("stats"))
async def handle_stats(message: types.Message):
    """Обработчик команды /stats"""
    try:
        # Получаем статистику через API
        stats = await api_client.get_stats(message.from_user.id)
        
        # Формируем текст статистики
        total_time = stats.get('total_time_minutes', 0)
        hours = total_time // 60
        minutes = total_time % 60
        task_count = stats.get('task_count', 0)
        
        response_text = (
            f"📊 <b>Ваша статистика:</b>\n\n"
            f"📋 Всего задач: {task_count}\n"
            f"⏱️ Общее время: {hours}ч {minutes}м ({total_time} минут)\n"
        )
        
        # Добавляем статистику по задачам если есть
        task_stats = stats.get('task_stats', [])
        if task_stats:
            response_text += "\n<b>Топ задач по времени:</b>\n"
            for i, task_stat in enumerate(task_stats[:5], 1):
                response_text += (
                    f"{i}. {task_stat.get('task_title', 'N/A')} - "
                    f"{task_stat.get('total_minutes', 0)} минут\n"
                )
        
        await message.answer(response_text)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статистики: {str(e)}")
