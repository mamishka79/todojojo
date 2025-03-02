from aiogram import Router, F
from aiogram.types import Message
from utils import load_json

router = Router()

@router.message(F.text == "🏆 Рейтинг")
async def leaderboard_cmd(message: Message):
    users = load_json("data/users.json")
    sorted_users = sorted(users.items(), key=lambda x: x[1]["points"], reverse=True)
    text = "\n".join(f"{i+1}. {u[1]['name']} – {u[1]['points']} очков" for i, u in enumerate(sorted_users[:10]))
    await message.answer(f"🏆 Топ-игроков:\n{text}")
