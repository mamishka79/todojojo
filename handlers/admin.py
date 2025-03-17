from aiogram import Router, F
from aiogram.types import Message, FSInputFile
import json
import os
from utils import load_json

router = Router()

# Задайте свой Telegram ID здесь
ADMIN_IDS = [1982583714]  # замените 123456789 на ваш реальный Telegram ID

def format_json(data):
    # Форматируем JSON в красивый текст
    return json.dumps(data, indent=4, ensure_ascii=False)

@router.message(F.text == "/dump_users")
async def dump_users_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Access denied")
        return
    data = load_json("data/users.json")
    text = format_json(data)
    if len(text) > 4000:
        if os.path.exists("data/users.json"):
            await message.answer_document(FSInputFile("data/users.json"), caption="Users Data")
        else:
            await message.answer("Users file not found.")
    else:
        await message.answer(f"Users Data:\n{text}")

@router.message(F.text == "/dump_tasks")
async def dump_tasks_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Access denied")
        return
    data = load_json("data/tasks.json")
    text = format_json(data)
    if len(text) > 4000:
        if os.path.exists("data/tasks.json"):
            await message.answer_document(FSInputFile("data/tasks.json"), caption="Tasks Data")
        else:
            await message.answer("Tasks file not found.")
    else:
        await message.answer(f"Tasks Data:\n{text}")

@router.message(F.text == "/dump_groups")
async def dump_groups_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Access denied")
        return
    data = load_json("data/groups.json")
    text = format_json(data)
    if len(text) > 4000:
        if os.path.exists("data/groups.json"):
            await message.answer_document(FSInputFile("data/groups.json"), caption="Groups Data")
        else:
            await message.answer("Groups file not found.")
    else:
        await message.answer(f"Groups Data:\n{text}")
