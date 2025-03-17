from aiogram import Router, F
from aiogram.types import Message
from utils import load_json, get_user

router = Router()


def get_translation(lang, key, **kwargs):
    translations = {
        "leaderboard_header": {
            "ru": "🏆 Топ-игроков:\n",
            "en": "🏆 Top Players:\n"
        },
        "points_format": {
            "ru": "{num}. {name} – {points} очков",
            "en": "{num}. {name} – {points} points"
        }
    }
    text = translations.get(key, {}).get(lang, "")
    if kwargs:
        text = text.format(**kwargs)
    return text


@router.message(F.text.in_(["🏆 Рейтинг", "🏆 Leaderboard"]))
async def leaderboard_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    users = load_json("data/users.json")
    sorted_users = sorted(users.items(), key=lambda x: x[1]["points"], reverse=True)

    header = get_translation(lang, "leaderboard_header")
    lines = [
        get_translation(lang, "points_format", num=i + 1, name=user_data["name"], points=user_data["points"])
        for i, (_, user_data) in enumerate(sorted_users[:10])
    ]
    text = header + "\n".join(lines)
    await message.answer(text)
