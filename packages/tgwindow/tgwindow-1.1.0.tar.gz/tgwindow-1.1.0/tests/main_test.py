import asyncio

from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, KeyboardButton

from src.middleware import WindowMiddleware
from src.window.base import BaseWindow
from src.window.wrapper import auto_window

dp = Dispatcher()


class Example(BaseWindow):
    #Buttons
    FIRST_BUTTON = InlineKeyboardButton(text="Button 1", callback_data="button_1")
    SECOND_BUTTON = InlineKeyboardButton(text="Button 2", callback_data="button_2")
    BUTTON_WITH_URL = InlineKeyboardButton(text="GitHub project", url="https://github.com/belyankiss/tgwindow")
    THIRD_BUTTON = KeyboardButton(text="Button 3")
    FOUR_BUTTON = KeyboardButton(text="Button 4")
    BACK_BUTTON = InlineKeyboardButton(text="BACK", callback_data="start")


    @auto_window
    async def hello(self, username: str):
        """
        Можно добавлять фото и передавать в метод любые аргументы для приятной работы!!!
        Args:
            username: Как пример

        Returns:

        """
        # self.photo = "Path:/to/your/photo.jpg"
        self.text = f"Hello {username}"
        self.button(self.FIRST_BUTTON)
        self.button(self.SECOND_BUTTON)

    @auto_window
    async def reply(self):
        self.text = "This is reply keyboard"
        self.button(self.THIRD_BUTTON)
        self.button(self.FOUR_BUTTON)

    @auto_window
    async def inline_button(self):
        self.text = "This message with inline keyboard"
        self.button(self.BUTTON_WITH_URL)

    @auto_window
    async def with_back_button(self):
        self.text = "Hello again!!!"
        self.button(self.BUTTON_WITH_URL)
        self.button(self.BACK_BUTTON)

    async def for_example(self):
        self.text = "Если вы хотите отправить самостоятельно, без автоотправки!"
        self.button(self.FIRST_BUTTON)
        self.button(self.SECOND_BUTTON)
        self.button(self.BUTTON_WITH_URL)
        self.size_keyboard = 2



async def main():
    bot = Bot("YOUR_BOT_TOKEN")
    "Здесь добавляем middleware, чтобы сообщения отправлялись автоматически"
    dp.update.middleware(WindowMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



@dp.message(F.text == "/start")
@dp.callback_query(F.data == Example.BACK_BUTTON.callback_data)
async def hello_message(event: Message | CallbackQuery, example: Example):
    username = event.from_user.username
    await example.hello(event, username=username)

@dp.callback_query(F.data == Example.SECOND_BUTTON.callback_data)
async def answer_with_reply_keyboard(call: CallbackQuery, example: Example):
    await example.inline_button(call)

@dp.callback_query(F.data == Example.FIRST_BUTTON.callback_data)
async def any_message(msg: Message, example: Example):
    await example.reply(msg)

@dp.message(F.text == Example.THIRD_BUTTON.text)
async def answer_reply_button(msg: Message, example: Example):
    await example.with_back_button(msg)

@dp.message()
async def example_send(msg: Message, example: type[Example]):
    example = example()
    await example.for_example()
    text, reply_markup = example.message()
    await msg.answer(text=text, reply_markup=reply_markup)




if __name__ == '__main__':
    asyncio.run(main())

