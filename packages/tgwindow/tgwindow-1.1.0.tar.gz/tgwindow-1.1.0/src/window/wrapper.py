from functools import wraps
from typing import Callable, Coroutine, Any

from aiogram.types import Message, CallbackQuery

from src.sender.sender import Send
from src.window.base import RegisterWindow


def auto_window(func: Callable[..., Coroutine[Any, Any, None]]) -> Callable[..., Coroutine[Any, Any, None]]:
    """
        Декоратор для автоматической работы с окнами.

        При вызове метода окна:
        1. Создает новый экземпляр окна на основе имени класса метода.
        2. Вызывает переданную функцию (метод окна).
        3. Формирует сообщение и клавиатуру через метод message().
        4. Отправляет сообщение с помощью Send.

        Args:
            func: Асинхронная функция окна.

        Returns:
            Асинхронная обертка функции.
        """
    @wraps(func)
    async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
        class_name = func.__qualname__.split(".")[0].lower()
        register = RegisterWindow()
        self = register.windows[class_name]()
        await func(self, *args, **kwargs)
        text, reply_markup = self.message()
        sender = Send(event=event, text=text, reply_markup=reply_markup, photo=self.photo)
        await sender()
    return wrapper