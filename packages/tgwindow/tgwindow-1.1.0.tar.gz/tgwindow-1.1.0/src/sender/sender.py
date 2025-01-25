import logging
import aiofiles

from aiogram.types import (Message,
                           CallbackQuery,
                           ReplyKeyboardMarkup,
                           InlineKeyboardMarkup,
                           ReplyKeyboardRemove,
                           BufferedInputFile)
from pydantic_core import ValidationError



class Send:
    def __init__(self, event: Message | CallbackQuery,
                 text: str,
                 reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | ReplyKeyboardRemove | None = None,
                 photo: str = None):
        self.event: Message | CallbackQuery = event
        self.text: str = text
        self.reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | ReplyKeyboardRemove | None = reply_markup
        self.photo: str | None = photo

    async def _sender(self):
        if isinstance(self.event, Message):
            await self._is_message()
        else:
            await self._is_callback()

    async def _is_message(self):
        if self.photo is not None:
            await self.event.answer_photo(photo=self.photo, caption=self.text, reply_markup=self.reply_markup)
        else:
            await self.event.answer(text=self.text, reply_markup=self.reply_markup)

    async def _is_callback(self):
        self.event: CallbackQuery
        try:
            if self.event.message.caption is not None:
                await self.event.message.edit_caption(caption=self.text, reply_markup=self.reply_markup)
            else:
                await self.event.message.edit_text(text=self.text, reply_markup=self.reply_markup)
        except ValidationError:
            await self.event.message.answer(text=self.text, reply_markup=self.reply_markup)

    async def _reformat_photo(self):
        try:
            async with aiofiles.open(file=self.photo, mode="rb") as photo:
                photo_byte = BufferedInputFile(file=await photo.read(), filename="photo")
                self.photo = photo_byte
        except FileNotFoundError:
            await self.event.answer_photo(photo=self.photo, caption=self.text, reply_markup=self.reply_markup)

    def __repr__(self):
        return f"Event: {type(self.event)} Text: {self.text} Reply markup: {self.reply_markup} Photo: {self.photo}"


    async def __call__(self):
        if self.photo is not None:
            await self._reformat_photo()
        await self._sender()