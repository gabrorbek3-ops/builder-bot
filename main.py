import asyncio
import os
import json
import subprocess
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Document
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from settings import settings


# ================== CONFIG ==================
ADMINS = [123456789]  # <-- O'Z TELEGRAM ID INGIZNI QO'YING
BOTS_DIR = "bots"
ACTIVE_FILE = "active_bots.json"

os.makedirs(BOTS_DIR, exist_ok=True)


# ================== BOT INIT ==================
bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# ================== STATES ==================
class BotCreate(StatesGroup):
    token = State()
    template = State()


# ================== HELPERS ==================
def get_templates():
    return [
        f.replace(".py", "")
        for f in os.listdir(BOTS_DIR)
        if f.endswith(".py")
    ]


def save_bot(token: str, template: str):
    bots = []
    if os.path.exists(ACTIVE_FILE):
        with open(ACTIVE_FILE, "r", encoding="utf-8") as f:
            bots = json.load(f)

    bots.append({
        "token": token,
        "template": template
    })

    with open(ACTIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(bots, f, indent=2)


def restore_bots():
    if not os.path.exists(ACTIVE_FILE):
        return

    with open(ACTIVE_FILE, "r", encoding="utf-8") as f:
        bots = json.load(f)

    for b in bots:
        env = os.environ.copy()
        env["BOT_TOKEN"] = b["token"]

        subprocess.Popen(
            ["python", f"{BOTS_DIR}/{b['template']}.py"],
            env=env
        )

    print("♻️ Oldingi botlar tiklandi")


# ================== HANDLERS ==================
@dp.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await message.answer(
        "🤖 Bot Manager\n\n"
        "Yangi bot qo‘shish uchun bot tokenini yuboring.\n"
        "Template yuklash uchun .py fayl yuboring (admin)."
    )
    await state.set_state(BotCreate.token)


@dp.message(BotCreate.token)
async def get_token(message: Message, state: FSMContext):
    await state.update_data(token=message.text)

    templates = get_templates()
    if not templates:
        return await message.answer("❌ Hech qanday template topilmadi")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t in templates],
        resize_keyboard=True
    )

    await message.answer(
        "🧩 Bot shablonini tanlang:",
        reply_markup=keyboard
    )
    await state.set_state(BotCreate.template)


@dp.message(BotCreate.template)
async def run_bot(message: Message, state: FSMContext):
    template = message.text
    if template not in get_templates():
        return await message.answer("❌ Bunday template yo‘q")
    bot_file = f"{BOTS_DIR}/{template}.py"

    if not os.path.exists(bot_file):
        return await message.answer("❌ Bunday template yo‘q")

    data = await state.get_data()
    token = data["token"]

    env = os.environ.copy()
    env["BOT_TOKEN"] = token

    save_bot(token, template)

    subprocess.Popen(
        ["python", bot_file],
        env=env
    )

    await message.answer(
        f"✅ Bot ishga tushdi!\n\n"
        f"🤖 Template: {template}"
    )

    await state.clear()


# ================== TEMPLATE UPLOAD ==================
@dp.message(F.document)
async def upload_template(message: Message):
    if message.from_user is None:
        return await message.answer("❌ User topilmadi")
    if message.from_user.id not in ADMINS:
        return await message.answer("❌ Siz admin emassiz")

    if message.document is None:
        return await message.answer("❌ Document topilmadi")
    
    doc: Document = message.document

    if doc.file_name is None:
        return await message.answer("❌ Fayl nomi topilmadi")

    if not doc.file_name.endswith(".py"):
        return await message.answer("❌ Faqat .py fayl yuboring")

    file_path = f"{BOTS_DIR}/{doc.file_name}"

    await bot.download(doc, destination=file_path)

    await message.answer(
        f"✅ Yangi template qo‘shildi:\n"
        f"`{doc.file_name.replace('.py','')}`",
        parse_mode="Markdown"
    )


# ================== RUN ==================
async def main():
    print("🚀 Manager bot ishga tushdi")
    restore_bots()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
