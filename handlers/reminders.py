from aiogram import Router, F
from aiogram.types import Message
from utils import ADMIN_IDS, load_json, get_user  # или как у вас функции называются

router = Router()

@router.message(F.text.startswith("/dm "))
async def dm_user_cmd(message: Message):
    """ Отправляет личное сообщение конкретному пользователю. 
        Формат: /dm <user_id> <текст сообщения>
    """
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Access denied")
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Использование: /dm <user_id> <текст>")
        return

    user_id_str = parts[1]
    text_to_send = parts[2]

    # Попробуем преобразовать user_id в int
    try:
        user_id = int(user_id_str)
    except ValueError:
        await message.answer("user_id должно быть числом (ID пользователя).")
        return

    # Проверим, зарегистрирован ли этот пользователь
    users = load_json("data/users.json")  # Или используйте вашу функцию get_user()
    if str(user_id) not in users:
        await message.answer(f"Пользователь с ID {user_id} не найден в базе.")
        return

    # Пробуем отправить сообщение в личку
    try:
        await message.bot.send_message(chat_id=user_id, text=text_to_send)
        await message.answer(f"Сообщение отправлено пользователю {user_id}.")
    except Exception as e:
        await message.answer(f"Ошибка отправки сообщения: {e}")
