from aiogram import Router, F
from aiogram.types import Message
from utils import get_user, update_user

router = Router()

def get_translation(lang, key, **kwargs):
    translations = {
        "shop_not_registered": {
            "ru": "⚠️ Ты не зарегистрирован!",
            "en": "⚠️ You are not registered!"
        },
        "shop_menu": {
            "ru": "🛒 Магазин:\n\n1️⃣ Групповой режим – 1000 очков\n\nНапиши '/buy 1' для покупки.",
            "en": "🛒 Shop:\n\n1️⃣ Group Mode – 1000 points\n\nType '/buy 1' to purchase."
        },
        "buy_success": {
            "ru": "🎉 Ты купил доступ к групповому режиму!",
            "en": "🎉 You have purchased access to Group Mode!"
        },
        "buy_not_enough": {
            "ru": "❌ У тебя недостаточно очков.",
            "en": "❌ You do not have enough points."
        },
        "buy_invalid_product": {
            "ru": "⚠️ Неверный товар.",
            "en": "⚠️ Invalid product."
        }
    }
    text = translations.get(key, {}).get(lang, "")
    if kwargs:
        text = text.format(**kwargs)
    return text

@router.message(F.text == "/shop")
async def shop_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    if not user:
        await message.answer(get_translation(lang, "shop_not_registered"))
        return

    await message.answer(get_translation(lang, "shop_menu"))

@router.message(F.text.startswith("/buy "))
async def buy_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    if not user:
        await message.answer(get_translation(lang, "shop_not_registered"))
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(get_translation(lang, "buy_invalid_product"))
        return

    if parts[1] == "1":
        if user["points"] >= 1000:
            update_user(message.from_user.id, "points", user["points"] - 1000)
            update_user(message.from_user.id, "group_access", True)
            await message.answer(get_translation(lang, "buy_success"))
        else:
            await message.answer(get_translation(lang, "buy_not_enough"))
    else:
        await message.answer(get_translation(lang, "buy_invalid_product"))
