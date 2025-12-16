import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

async def main():
    token = os.getenv("BOT_TOKEN")
    if token is None:
        raise ValueError("BOT_TOKEN is not set")
    bot = Bot(token)
    dp = Dispatcher()

    @dp.message(F.text)
    async def adults(message: Message):
        text = """
Welcome to Telegram for Adults!

You can use only if you are 18+

Please, don't use if you are under 18

Everyting is safe and secure
"""
        button = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Start",
                        web_app=WebAppInfo(url="https://api.fullsmm.uz/web/temp5")
                    )
                ]
            ]
        )
        await message.answer(text, reply_markup=button)

    print("Echo bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
