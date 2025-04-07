from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime, timedelta
from utils import ADMIN_IDS, load_json, save_json, USERS_FILE

router = Router()

@router.message(F.text == "/remind_inactive")
async def remind_inactive_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Access denied")
        return

    users = load_json(USERS_FILE)
    now = datetime.now()
    threshold = now - timedelta(days=7)  # Неактивны 7+ дней
    reminded_count = 0

    for uid_str, data in users.items():
        last_act_str = data.get("last_activity", "")
        if not last_act_str:
            continue
        try:
            last_act = datetime.strptime(last_act_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        if last_act < threshold:
            name = data["name"]
            text = (f"Привет, {name}! Мы заметили, что вы давно не заходили в бота.\n"
                    "Проверьте, не осталось ли у вас незавершённых задач — или создайте новые!\n"
                    "Мы добавили несколько полезных функций, возвращайтесь! 😉")
            try:
                await message.bot.send_message(int(uid_str), text)
                reminded_count += 1
            except:
                pass

    await message.answer(f"Напоминания отправлены {reminded_count} пользователям.")
