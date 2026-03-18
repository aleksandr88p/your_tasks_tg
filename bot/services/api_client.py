"""
API клиент для работы с YourTasks API
"""
import aiohttp
from typing import List, Dict, Any, Optional
from config.settings import settings

class YourTasksAPIClient:
    """Клиент для взаимодействия с YourTasks API"""
    
    def __init__(self):
        self.base_url = settings.API_URL
        self.headers = {
            "Content-Type": "application/json",
        }
    
    def _get_auth_headers(self, telegram_id: int) -> Dict[str, str]:
        """Получить заголовки с аутентификацией"""
        headers = self.headers.copy()
        headers["telegram-user-id"] = str(telegram_id)  # Исправлено на telegram-user-id
        return headers
    
    async def create_task(self, telegram_id: int, title: str) -> Dict[str, Any]:
        """Создать новую задачу"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/tasks"
            headers = self._get_auth_headers(telegram_id)
            data = {"title": title}
            
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to create task: {response.status} - {error_text}")
    
    async def get_tasks(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Получить все задачи пользователя"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/tasks"
            headers = self._get_auth_headers(telegram_id)
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get tasks: {response.status} - {error_text}")
    
    async def get_task(self, telegram_id: int, task_id: int) -> Dict[str, Any]:
        """Получить конкретную задачу"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/tasks/{task_id}"
            headers = self._get_auth_headers(telegram_id)
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get task: {response.status} - {error_text}")
    
    async def update_task_status(self, telegram_id: int, task_id: int, status: str) -> Dict[str, Any]:
        """Обновить статус задачи"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/tasks/{task_id}/status"
            headers = self._get_auth_headers(telegram_id)
            data = {"status": status}
            
            async with session.patch(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to update task status: {response.status} - {error_text}")
    
    async def add_time(self, telegram_id: int, task_id: int, minutes: int, comment: str = "") -> Dict[str, Any]:
        """Добавить время к задаче"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/timelogs"
            headers = self._get_auth_headers(telegram_id)
            data = {
                "task_id": task_id,
                "minutes": minutes,
                "comment": comment
            }
            
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to add time: {response.status} - {error_text}")
    
    async def get_timelogs(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Получить все логи времени пользователя"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/timelogs"
            headers = self._get_auth_headers(telegram_id)
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get timelogs: {response.status} - {error_text}")
    
    async def get_stats(self, telegram_id: int) -> Dict[str, Any]:
        """Получить общую статистику пользователя"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/stats/summary"
            headers = self._get_auth_headers(telegram_id)
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get stats: {response.status} - {error_text}")

# Глобальный экземпляр клиента
api_client = YourTasksAPIClient()
