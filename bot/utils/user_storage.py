"""
Простое хранилище данных пользователей в памяти
"""
from typing import Dict

# Временное хранилище для языков пользователей
# В продакшене заменить на БД
user_languages: Dict[int, str] = {}

def set_user_language(user_id: int, language: str) -> None:
    """Установить язык пользователя"""
    user_languages[user_id] = language

def get_user_language(user_id: int) -> str:
    """Получить язык пользователя"""
    return user_languages.get(user_id, "ru")  # По умолчанию русский
