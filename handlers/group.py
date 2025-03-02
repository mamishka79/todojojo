import os
import json
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils import get_user, update_user, load_json, save_json, add_user

router = Router()

GROUPS_FILE = "data/groups.json"

if not os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

def get_groups():
    return load_json(GROUPS_FILE)

def save_groups(data):
    save_json(GROUPS_FILE, data)

@router.message(Command("start_group"))
async def start_group_cmd(message: Message):
    # Регистрируем пользователя, если он ещё не зарегистрирован
    user = get_user(message.from_user.id)
    if not user:
        add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
        user = get_user(message.from_user.id)

    chat_id = str(message.chat.id)
    groups = get_groups()

    # Если группа уже активирована
    if chat_id in groups:
        # Если вызывающий пользователь не числится в группе, добавляем его без списания очков
        if message.from_user.id not in groups[chat_id]["users"]:
            groups[chat_id]["users"].append(message.from_user.id)
            save_groups(groups)
            await message.answer("✅ Групповой режим уже активирован! Вы были добавлены в группу.")
        else:
            await message.answer("✅ Групповой режим уже активирован!")
        return

    # Если группы ещё нет – создаём новую
    if user["points"] < 120:
        await message.answer("❌ У тебя недостаточно очков для группового режима (нужно 120).")
        return

    groups[chat_id] = {
        "users": [],
        "tasks": [],
        "confirmations": {}
    }
    # Добавляем инициатора группы и списываем 1000 очков
    groups[chat_id]["users"].append(message.from_user.id)
    save_groups(groups)
    update_user(message.from_user.id, "points", user["points"] - 120)
    await message.answer(
        "🎉 Групповой режим активирован! Теперь участники могут присоединиться, отправив команду /join_group."
    )

@router.message(Command("help_group"))
async def help_group_cmd(message: Message):
    help_text = (
        "Инструкции для группового режима:\n\n"
        "/start_group – активировать групповой режим (требуется 1000 очков).\n"
        "/join_group – присоединиться к уже активированному групповому режиму.\n"
        "/add_task <текст задачи> – добавить задачу в группу (автор задачи сохраняется).\n"
        "/group_tasks – показать список групповых задач с нумерацией и указанием автора.\n"
        "/group_tasks_by <username> – показать список групповых задач с нумерацией указанного автора.\n"
        "/done <номер задачи> – завершить задачу (только автор; требуется подтверждение большинства участников).\n"
        "/edit_task <номер задачи> <новый текст> – редактировать задачу (только автор).\n"
        "/delete_task <номер задачи> – удалить задачу (только автор).\n"
        "/group_members – показать список участников группы.\n"
        "/leave_group – выйти из группового режима.\n"
        "/help_group – показать эту справку."
    )
    await message.answer(help_text)

@router.message(Command("join_group"))
async def join_group_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован. Запустите /start_group")
        return

    if message.from_user.id in groups[chat_id]["users"]:
        await message.answer("ℹ️ Вы уже состоите в группе.")
        return

    groups[chat_id]["users"].append(message.from_user.id)
    save_groups(groups)
    if not get_user(message.from_user.id):
        add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer("✅ Вы успешно присоединились к группе!")

@router.message(Command("add_task"))
async def add_group_task_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован. Введите /start_group")
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer("⚠️ Вы не состоите в группе. Присоединитесь через /join_group")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer("⚠️ Укажите текст задачи после команды /add_task")
        return
    task_text = parts[1].strip()
    groups[chat_id]["tasks"].append({
        "task": task_text,
        "done": False,
        "creator": message.from_user.id
    })
    save_groups(groups)
    await message.answer(f"✅ Групповая задача добавлена:\n👉 {task_text}")

@router.message(Command("group_tasks"))
async def group_tasks_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован. Запустите /start_group")
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer("⚠️ Вы не состоите в группе. Присоединитесь через /join_group")
        return

    tasks = groups[chat_id]["tasks"]
    if not tasks:
        await message.answer("ℹ️ В группе пока нет задач.")
        return

    task_list = "\n".join(
        f"{i+1}. {'✅' if task['done'] else '❌'} {task['task']} (от {get_user(task['creator'])['name']})"
        for i, task in enumerate(tasks)
    )
    await message.answer(f"📋 Групповые задачи:\n{task_list}")

from aiogram.filters import Command

@router.message(Command("group_tasks_by"))
async def group_tasks_by_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован. Запустите /start_group")
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer("⚠️ Вы не состоите в группе. Присоединитесь через /join_group")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Используй: /group_tasks_by <username или имя>")
        return

    args = parts[1].strip()
    if not args:
        await message.answer("⚠️ Используй: /group_tasks_by <username или имя>")
        return

    target_id = None
    # Ищем пользователя среди участников группы по username (без @) или по имени
    for uid in groups[chat_id]["users"]:
        u = get_user(uid)
        if u:
            if u.get("username", "").lower() == args.lstrip("@").lower() or u["name"].lower() == args.lower():
                target_id = uid
                break

    if target_id is None:
        await message.answer("⚠️ Пользователь с таким именем не найден в группе.")
        return

    # Фильтруем задачи, добавленные этим пользователем
    tasks = groups[chat_id]["tasks"]
    user_tasks = [(i, task) for i, task in enumerate(tasks) if task.get("creator") == target_id]
    if not user_tasks:
        await message.answer("ℹ️ У выбранного пользователя нет задач.")
        return

    task_list = "\n".join(
        f"{i+1}. {'✅' if task['done'] else '❌'} {task['task']}"
        for i, task in user_tasks
    )
    target = get_user(target_id)
    await message.answer(f"📋 Задачи пользователя {target['name']}:\n{task_list}")

@router.message(Command("done"))
async def group_done_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован.")
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer("⚠️ Вы не состоите в группе. Присоединитесь через /join_group")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Укажите номер задачи после команды /done")
        return
    try:
        task_index = int(parts[1].strip()) - 1
    except ValueError:
        await message.answer("⚠️ Неверный номер задачи.")
        return
    if not (0 <= task_index < len(groups[chat_id]["tasks"])):
        await message.answer("⚠️ Неверный номер задачи.")
        return
    task = groups[chat_id]["tasks"][task_index]
    if message.from_user.id != task.get("creator"):
        await message.answer("⚠️ Только автор задачи может её завершить.")
        return
    confirmations = groups[chat_id]["confirmations"].setdefault(str(task_index), [])
    if message.from_user.id in confirmations:
        await message.answer("ℹ️ Вы уже подтвердили выполнение этой задачи.")
        return
    else:
        confirmations.append(message.from_user.id)
    if len(set(confirmations)) >= (len(groups[chat_id]["users"]) + 1) // 2:
        groups[chat_id]["tasks"][task_index]["done"] = True
        for user_id in groups[chat_id]["users"]:
            update_user(user_id, "points", get_user(user_id)["points"] + 5)
        await message.answer(f"✅ Задача '{task['task']}' завершена! Всем участникам начислено +5 очков.")
    else:
        await message.answer("🕓 Ожидание подтверждения большинства участников...")
    save_groups(groups)

@router.message(Command("edit_task"))
async def edit_group_task_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован. Введите /start_group")
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer("⚠️ Вы не состоите в группе. Присоединитесь через /join_group")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("⚠️ Используй: /edit_task <номер задачи> <новый текст>")
        return
    try:
        task_index = int(parts[1].strip()) - 1
    except ValueError:
        await message.answer("⚠️ Неверный номер задачи.")
        return
    new_text = parts[2].strip()
    if not (3 <= len(new_text) <= 100):
        await message.answer("⚠️ Текст задачи должен быть от 3 до 100 символов.")
        return
    if not (0 <= task_index < len(groups[chat_id]["tasks"])):
        await message.answer("⚠️ Неверный номер задачи.")
        return
    task = groups[chat_id]["tasks"][task_index]
    if message.from_user.id != task.get("creator"):
        await message.answer("⚠️ Только автор задачи может её редактировать.")
        return
    task["task"] = new_text
    save_groups(groups)
    await message.answer(f"✅ Задача {task_index+1} успешно отредактирована.")

@router.message(Command("delete_task"))
async def delete_group_task_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован. Введите /start_group")
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer("⚠️ Вы не состоите в группе. Присоединитесь через /join_group")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("⚠️ Используй: /delete_task <номер задачи>")
        return
    try:
        task_index = int(parts[1].strip()) - 1
    except ValueError:
        await message.answer("⚠️ Неверный номер задачи.")
        return
    if not (0 <= task_index < len(groups[chat_id]["tasks"])):
        await message.answer("⚠️ Неверный номер задачи.")
        return
    task = groups[chat_id]["tasks"][task_index]
    if message.from_user.id != task.get("creator"):
        await message.answer("⚠️ Только автор задачи может её удалить.")
        return
    groups[chat_id]["tasks"].pop(task_index)
    if str(task_index) in groups[chat_id]["confirmations"]:
        del groups[chat_id]["confirmations"][str(task_index)]
    save_groups(groups)
    await message.answer(f"✅ Задача {task_index+1} удалена.")

@router.message(Command("group_members"))
async def group_members_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован.")
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer("⚠️ Вы не состоите в группе. Присоединитесь через /join_group")
        return

    members = groups[chat_id]["users"]
    if not members:
        await message.answer("ℹ️ В группе пока нет участников.")
        return

    members_text = "\n".join(
        f"{i + 1}. {get_user(member)['name']} {f'(@{get_user(member)['username']})' if get_user(member).get('username') else ''}"
        for i, member in enumerate(members)
    )
    await message.answer(f"👥 Участники группы:\n{members_text}")

@router.message(Command("leave_group"))
async def leave_group_cmd(message: Message):
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer("⚠️ Групповой режим не активирован.")
        return

    if message.from_user.id in groups[chat_id]["users"]:
        groups[chat_id]["users"].remove(message.from_user.id)
        save_groups(groups)
        await message.answer("✅ Вы покинули групповой режим.")
    else:
        await message.answer("ℹ️ Вы не состоите в группе.")
