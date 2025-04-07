from aiogram import Router, F
from aiogram.types import Message, FSInputFile
import json
import os
from datetime import datetime, timedelta
from utils import (
    load_json, save_json, USERS_FILE, ADMIN_IDS,
    get_user_list, get_user
)

router = Router()

def format_json(data):
    return json.dumps(data, indent=4, ensure_ascii=False)

@router.message(F.text == "/dump_users")
async def dump_users_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Access denied")
        return
    data = load_json(USERS_FILE)
    text = format_json(data)
    if len(text) > 4000:
        if os.path.exists(USERS_FILE):
            await message.answer_document(FSInputFile(USERS_FILE), caption="Users Data")
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


@router.message(F.text.startswith("/broadcast"))
async def broadcast_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Access denied")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /broadcast <your message>")
        return

    broadcast_text = parts[1].strip()
    if not broadcast_text:
        await message.answer("Message is empty.")
        return

    users = get_user_list()
    count = 0
    for uid in users:
        try:
            await message.bot.send_message(uid, broadcast_text)
            count += 1
        except:
            pass

    await message.answer(f"Broadcast delivered to {count} users.")