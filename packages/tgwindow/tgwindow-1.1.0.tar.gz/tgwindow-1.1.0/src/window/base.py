from typing import Union, Optional

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import (InlineKeyboardMarkup,
                           ReplyKeyboardMarkup,
                           ReplyKeyboardRemove,
                           InlineKeyboardButton,
                           KeyboardButton)

from src.errors import EmptyTextError, WrongFormatError


class BaseWindow:
    def __init__(self):
        """
            text - текст сообщения. Поле не может быть пустым.
            size_keyboard - размер клавиатуры
            photo - ссылка на телеграм фото или путь к файлу фото
        """
        self.text: str | None = None
        self._reply: list[list[Optional[KeyboardButton, ...]]] = []
        self._inline: list[list[Optional[InlineKeyboardButton, ...]]] = []
        self.size_keyboard: Optional[int] = None
        self.photo: Optional[str] = None
        self.delete_keyboard: bool = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        window = RegisterWindow()
        window.add(cls)

    def button(self, button: Union[KeyboardButton, InlineKeyboardButton]) -> None:
        """Добавляет одну кнопку."""
        if isinstance(button, KeyboardButton):
            self._reply.append([button])
        else:
            self._inline.append([button])

    def _create_kb(self):
        """
        Создает Inline или Reply клавиатуру, в зависимости от условий. Если есть size_keyboard,
        то он будет разделять клавиатуру по колонкам.
        Returns:

        """
        if self._reply:
            if self.size_keyboard is not None:
                kb = ReplyKeyboardBuilder()
                for button in self._reply:
                    kb.add(button[0])
                return kb.adjust(self.size_keyboard).as_markup(resize_keyboard=True)
            return ReplyKeyboardMarkup(keyboard=self._reply, resize_keyboard=True)
        if self._inline:
            if self.size_keyboard is not None:
                kb = InlineKeyboardBuilder()
                for button in self._inline:
                    kb.add(button[0])
                return kb.adjust(self.size_keyboard).as_markup()
            return InlineKeyboardMarkup(inline_keyboard=self._inline)
        return []


    def message(self) -> tuple[str, Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove]]:
        """Возвращает сообщение с клавиатурой или без клавиатуры."""
        if not self.text:
            raise EmptyTextError("Текст сообщения должен быть обязательно!")

        # Проверка на смешение inline и reply кнопок
        if self._reply and self._inline:
            raise WrongFormatError("Должны быть переданы только inline или только reply кнопки")

        if self.delete_keyboard:
            kb = ReplyKeyboardRemove()
        else:
            kb = self._create_kb()

        # Генерация клавиатуры и возврат сообщения
        return self.text, kb

    def __repr__(self):
        return (f"Text: {self.text}\n"
                f"Keyboard: {self._reply or self._inline}\n"
                f"Photo: {self.photo}")



class RegisterWindow:
    _instance = None
    windows: dict[str, type["BaseWindow"]] = {}
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def add(cls, window: type["BaseWindow"]):
        cls.windows[window.__name__.lower()] = window

    def __repr__(self):
        return f"{self.windows}"











