from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.window.base import RegisterWindow, BaseWindow


class WindowMiddleware(BaseMiddleware):
    """
    Используется для автоматического добавления созданных окон в handlers. Использование классов своих окон возможно
    только по названию вашего класса в малом регистре.
    """
    def __init__(self):
        super().__init__()

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ):
        window = RegisterWindow()
        for key, value in window.windows.items():
            key: str
            value: BaseWindow
            data[key] = value
        return await handler(event, data)