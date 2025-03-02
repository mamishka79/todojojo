from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils import add_report, load_json

router = Router()

@router.message(Command("report"))
async def report_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("⚠️ Используй: `/report <имя пользователя>`")
        return

    reported_name = parts[1].strip()
    reported_id = None

    users = load_json("data/users.json")
    for user_id, data in users.items():
        if data["name"].lower() == reported_name.lower():
            reported_id = user_id
            break

    if reported_id is None:
        await message.answer("⚠️ Пользователь не найден.")
        return

    result = add_report(message.from_user.id, reported_id)
    if result == "already_reported":
        await message.answer(f"ℹ️ Вы уже пожаловались на {reported_name}.")
    elif result is True:
        await message.answer(f"⚠️ {reported_name} получил 3+ жалобы! Минус 10 очков!")
    else:
        await message.answer(f"🚨 Жалоба на {reported_name} отправлена.")
