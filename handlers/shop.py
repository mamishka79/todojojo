from aiogram import Router, F
from aiogram.types import Message
from utils import get_user, update_user

router = Router()

@router.message(F.text == "/shop")
async def shop_cmd(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("⚠️ Ты не зарегистрирован!")
        return

    await message.answer("🛒 Магазин:\n\n1️⃣ Групповой режим – 1000 очков\n\nНапиши '/buy 1' для покупки.")

@router.message(F.text.startswith("/buy "))
async def buy_cmd(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("⚠️ Ты не зарегистрирован!")
        return

    if message.text.split()[1] == "1":
        if user["points"] >= 1000:
            update_user(message.from_user.id, "points", user["points"] - 1000)
            update_user(message.from_user.id, "group_access", True)
            await message.answer("🎉 Ты купил доступ к групповому режиму!")
        else:
            await message.answer("❌ У тебя недостаточно очков.")
    else:
        await message.answer("⚠️ Неверный товар.")
