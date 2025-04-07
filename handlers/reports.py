from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils import add_report, load_json, get_user, update_last_activity

router = Router()

def get_translation(lang, key, **kwargs):
    translations = {
        "report_usage": {
            "ru": "⚠️ Используй: `/report <имя пользователя>`",
            "en": "⚠️ Usage: `/report <username>`"
        },
        "user_not_found": {
            "ru": "⚠️ Пользователь не найден.",
            "en": "⚠️ User not found."
        },
        "already_reported": {
            "ru": "ℹ️ Вы уже пожаловались на {reported_name}.",
            "en": "ℹ️ You have already reported {reported_name}."
        },
        "report_threshold": {
            "ru": "⚠️ {reported_name} получил 3+ жалобы! Минус 10 очков!",
            "en": "⚠️ {reported_name} has received 3+ reports! Deducted 10 points!"
        },
        "report_submitted": {
            "ru": "🚨 Жалоба на {reported_name} отправлена.",
            "en": "🚨 Report on {reported_name} has been submitted."
        }
    }
    text = translations.get(key, {}).get(lang, "")
    if kwargs:
        text = text.format(**kwargs)
    return text

@router.message(Command("report"))
async def report_cmd(message: Message):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer(get_translation(lang, "report_usage"))
        return

    reported_name = parts[1].strip()
    reported_id = None

    users = load_json("data/users.json")
    for user_id, data in users.items():
        if data["name"].lower() == reported_name.lower():
            reported_id = user_id
            break

    if reported_id is None:
        await message.answer(get_translation(lang, "user_not_found"))
        return

    result = add_report(message.from_user.id, reported_id)
    if result == "already_reported":
        await message.answer(get_translation(lang, "already_reported", reported_name=reported_name))
    elif result is True:
        await message.answer(get_translation(lang, "report_threshold", reported_name=reported_name))
    else:
        await message.answer(get_translation(lang, "report_submitted", reported_name=reported_name))
