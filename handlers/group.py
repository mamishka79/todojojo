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

def get_translation(lang, key, **kwargs):
    translations = {
        "start_group_already_added": {
            "ru": "✅ Групповой режим уже активирован! Вы были добавлены в группу.",
            "en": "✅ Group mode is already activated! You have been added to the group."
        },
        "start_group_already": {
            "ru": "✅ Групповой режим уже активирован!",
            "en": "✅ Group mode is already activated!"
        },
        "start_group_not_enough_points": {
            "ru": "❌ У тебя недостаточно очков для группового режима (нужно 120).",
            "en": "❌ You do not have enough points for group mode (requires 120)."
        },
        "start_group_activated": {
            "ru": "🎉 Групповой режим активирован! Теперь участники могут присоединиться, отправив команду /join_group.",
            "en": "🎉 Group mode activated! Now participants can join by sending /join_group."
        },
        "help_group": {
            "ru": (
                "Инструкции для группового режима:\n\n"
                "/start_group – активировать групповой режим (требуется 120 очков).\n"
                "/join_group – присоединиться к уже активированному групповому режиму.\n"
                "/add_task <текст задачи> – добавить задачу в группу (автор задачи сохраняется).\n"
                "/group_tasks – показать список групповых задач с нумерацией и указанием автора.\n"
                "/group_tasks_by <username> – показать список задач указанного автора.\n"
                "/done <номер задачи> – завершить задачу (только автор; требуется подтверждение большинства участников).\n"
                "/edit_task <номер задачи> <новый текст> – редактировать задачу (только автор).\n"
                "/delete_task <номер задачи> – удалить задачу (только автор).\n"
                "/group_members – показать список участников группы.\n"
                "/leave_group – выйти из группы.\n"
                "/help_group – показать эту справку."
            ),
            "en": (
                "Group mode instructions:\n\n"
                "/start_group - Activate group mode (requires 120 points).\n"
                "/join_group - Join an activated group mode.\n"
                "/add_task <task text> - Add a group task (the task author is recorded).\n"
                "/group_tasks - Show the list of group tasks with numbering and author info.\n"
                "/group_tasks_by <username> - Show tasks of the specified user.\n"
                "/done <task number> - Complete the task (only the creator; requires majority confirmation).\n"
                "/edit_task <task number> <new text> - Edit the task (only the creator).\n"
                "/delete_task <task number> - Delete the task (only the creator).\n"
                "/group_members - Show the list of group members.\n"
                "/leave_group - Exit group mode.\n"
                "/help_group - Show this help message."
            )
        },
        "join_group_not_active": {
            "ru": "⚠️ Групповой режим не активирован. Запустите /start_group",
            "en": "⚠️ Group mode is not activated. Start it with /start_group."
        },
        "join_group_already": {
            "ru": "ℹ️ Вы уже состоите в группе.",
            "en": "ℹ️ You are already in the group."
        },
        "join_group_success": {
            "ru": "✅ Вы успешно присоединились к группе!",
            "en": "✅ You have successfully joined the group!"
        },
        "add_task_not_active": {
            "ru": "⚠️ Групповой режим не активирован. Введите /start_group",
            "en": "⚠️ Group mode is not activated. Start it with /start_group."
        },
        "add_task_not_in_group": {
            "ru": "⚠️ Вы не состоите в группе. Присоединитесь через /join_group",
            "en": "⚠️ You are not in the group. Join using /join_group."
        },
        "add_task_no_text": {
            "ru": "⚠️ Укажите текст задачи после команды /add_task",
            "en": "⚠️ Please provide the task text after the /add_task command."
        },
        "group_task_added": {
            "ru": "✅ Групповая задача добавлена:\n👉 {task_text}",
            "en": "✅ Group task added:\n👉 {task_text}"
        },
        "group_tasks_not_active": {
            "ru": "⚠️ Групповой режим не активирован. Запустите /start_group",
            "en": "⚠️ Group mode is not activated. Start it with /start_group."
        },
        "group_tasks_not_in_group": {
            "ru": "⚠️ Вы не состоите в группе. Присоединитесь через /join_group",
            "en": "⚠️ You are not in the group. Join using /join_group."
        },
        "group_tasks_empty": {
            "ru": "ℹ️ В группе пока нет задач.",
            "en": "ℹ️ There are currently no tasks in the group."
        },
        "group_tasks_header": {
            "ru": "📋 Групповые задачи:\n",
            "en": "📋 Group tasks:\n"
        },
        "by": {
            "ru": "(от {name})",
            "en": "(by {name})"
        },
        "group_tasks_by_usage": {
            "ru": "⚠️ Используй: /group_tasks_by <username или имя>",
            "en": "⚠️ Usage: /group_tasks_by <username or name>"
        },
        "group_tasks_by_not_found": {
            "ru": "⚠️ Пользователь с таким именем не найден в группе.",
            "en": "⚠️ User with that name was not found in the group."
        },
        "group_tasks_by_empty": {
            "ru": "ℹ️ У выбранного пользователя нет задач.",
            "en": "ℹ️ The selected user has no tasks."
        },
        "group_tasks_by_header": {
            "ru": "📋 Задачи пользователя {name}:\n",
            "en": "📋 Tasks of user {name}:\n"
        },
        "done_ask_number": {
            "ru": "⚠️ Укажите номер задачи после команды /done",
            "en": "⚠️ Please specify the task number after the /done command."
        },
        "done_invalid_number": {
            "ru": "⚠️ Неверный номер задачи.",
            "en": "⚠️ Invalid task number."
        },
        "done_only_creator": {
            "ru": "⚠️ Только автор задачи может её завершить.",
            "en": "⚠️ Only the task's creator can complete it."
        },
        "done_already_confirmed": {
            "ru": "ℹ️ Вы уже подтвердили выполнение этой задачи.",
            "en": "ℹ️ You have already confirmed completion of this task."
        },
        "done_waiting": {
            "ru": "🕓 Ожидание подтверждения большинства участников...",
            "en": "🕓 Waiting for majority confirmation from group members..."
        },
        "done_completed": {
            "ru": "✅ Задача '{task}' завершена! Всем участникам начислено +5 очков.",
            "en": "✅ Task '{task}' completed! +5 points have been awarded to all participants."
        },
        "edit_task_usage": {
            "ru": "⚠️ Используй: /edit_task <номер задачи> <новый текст>",
            "en": "⚠️ Usage: /edit_task <task number> <new text>"
        },
        "edit_task_invalid_number": {
            "ru": "⚠️ Неверный номер задачи.",
            "en": "⚠️ Invalid task number."
        },
        "edit_task_text_length": {
            "ru": "⚠️ Текст задачи должен быть от 3 до 100 символов.",
            "en": "⚠️ Task text must be between 3 and 100 characters."
        },
        "edit_task_success": {
            "ru": "✅ Задача {num} успешно отредактирована.",
            "en": "✅ Task {num} successfully edited."
        },
        "delete_task_usage": {
            "ru": "⚠️ Используй: /delete_task <номер задачи>",
            "en": "⚠️ Usage: /delete_task <task number>"
        },
        "delete_task_invalid_number": {
            "ru": "⚠️ Неверный номер задачи.",
            "en": "⚠️ Invalid task number."
        },
        "delete_task_not_creator": {
            "ru": "⚠️ Только автор задачи может её удалить.",
            "en": "⚠️ Only the task's creator can delete it."
        },
        "delete_task_success": {
            "ru": "✅ Задача {num} удалена.",
            "en": "✅ Task {num} deleted."
        },
        "group_members_not_active": {
            "ru": "⚠️ Групповой режим не активирован.",
            "en": "⚠️ Group mode is not activated."
        },
        "group_members_not_in_group": {
            "ru": "⚠️ Вы не состоите в группе. Присоединитесь через /join_group",
            "en": "⚠️ You are not in the group. Join using /join_group."
        },
        "group_members_empty": {
            "ru": "ℹ️ В группе пока нет участников.",
            "en": "ℹ️ There are currently no members in the group."
        },
        "group_members_header": {
            "ru": "👥 Участники группы:\n",
            "en": "👥 Group members:\n"
        },
        "leave_group_not_active": {
            "ru": "⚠️ Групповой режим не активирован.",
            "en": "⚠️ Group mode is not activated."
        },
        "leave_group_success": {
            "ru": "✅ Вы покинули групповой режим.",
            "en": "✅ You have left group mode."
        },
        "leave_group_not_in_group": {
            "ru": "ℹ️ Вы не состоите в группе.",
            "en": "ℹ️ You are not in the group."
        }
    }
    text = translations.get(key, {}).get(lang, "")
    if kwargs:
        text = text.format(**kwargs)
    return text

@router.message(Command("start_group"))
async def start_group_cmd(message: Message):
    # Регистрируем пользователя, если он ещё не зарегистрирован
    user = get_user(message.from_user.id)
    if not user:
        add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
        user = get_user(message.from_user.id)
    lang = user.get("language", "ru")

    chat_id = str(message.chat.id)
    groups = get_groups()

    if chat_id in groups:
        if message.from_user.id not in groups[chat_id]["users"]:
            groups[chat_id]["users"].append(message.from_user.id)
            save_groups(groups)
            await message.answer(get_translation(lang, "start_group_already_added"))
        else:
            await message.answer(get_translation(lang, "start_group_already"))
        return

    if user["points"] < 120:
        await message.answer(get_translation(lang, "start_group_not_enough_points"))
        return

    groups[chat_id] = {
        "users": [],
        "tasks": [],
        "confirmations": {}
    }
    groups[chat_id]["users"].append(message.from_user.id)
    save_groups(groups)
    update_user(message.from_user.id, "points", user["points"] - 120)
    await message.answer(get_translation(lang, "start_group_activated"))

@router.message(Command("help_group"))
async def help_group_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    help_text = get_translation(lang, "help_group")
    await message.answer(help_text)

@router.message(Command("join_group"))
async def join_group_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "join_group_not_active"))
        return

    if message.from_user.id in groups[chat_id]["users"]:
        await message.answer(get_translation(lang, "join_group_already"))
        return

    groups[chat_id]["users"].append(message.from_user.id)
    save_groups(groups)
    if not get_user(message.from_user.id):
        add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer(get_translation(lang, "join_group_success"))

@router.message(Command("add_task"))
async def add_group_task_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "add_task_not_active"))
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer(get_translation(lang, "add_task_not_in_group"))
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.answer(get_translation(lang, "add_task_no_text"))
        return
    task_text = parts[1].strip()
    groups[chat_id]["tasks"].append({
        "task": task_text,
        "done": False,
        "creator": message.from_user.id
    })
    save_groups(groups)
    await message.answer(get_translation(lang, "group_task_added", task_text=task_text))

@router.message(Command("group_tasks"))
async def group_tasks_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "group_tasks_not_active"))
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer(get_translation(lang, "group_tasks_not_in_group"))
        return

    tasks = groups[chat_id]["tasks"]
    if not tasks:
        await message.answer(get_translation(lang, "group_tasks_empty"))
        return

    task_list = "\n".join(
        f"{i+1}. {'✅' if task['done'] else '❌'} {task['task']} " +
        (get_translation(lang, "by", name=get_user(task['creator'])['name']))
        for i, task in enumerate(tasks)
    )
    await message.answer(f"{get_translation(lang, 'group_tasks_header')}{task_list}")

@router.message(Command("group_tasks_by"))
async def group_tasks_by_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "group_tasks_not_active"))
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer(get_translation(lang, "group_tasks_not_in_group"))
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(get_translation(lang, "group_tasks_by_usage"))
        return

    args = parts[1].strip()
    if not args:
        await message.answer(get_translation(lang, "group_tasks_by_usage"))
        return

    target_id = None
    for uid in groups[chat_id]["users"]:
        u = get_user(uid)
        if u:
            if u.get("username", "").lower() == args.lstrip("@").lower() or u["name"].lower() == args.lower():
                target_id = uid
                break

    if target_id is None:
        await message.answer(get_translation(lang, "group_tasks_by_not_found"))
        return

    tasks = groups[chat_id]["tasks"]
    user_tasks = [(i, task) for i, task in enumerate(tasks) if task.get("creator") == target_id]
    if not user_tasks:
        await message.answer(get_translation(lang, "group_tasks_by_empty"))
        return

    task_list = "\n".join(
        f"{i+1}. {'✅' if task['done'] else '❌'} {task['task']}"
        for i, task in user_tasks
    )
    target = get_user(target_id)
    await message.answer(get_translation(lang, "group_tasks_by_header", name=target["name"]) + task_list)

@router.message(Command("done"))
async def group_done_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "done_invalid_number"))
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer(get_translation(lang, "join_group_not_active"))
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(get_translation(lang, "done_ask_number"))
        return
    try:
        task_index = int(parts[1].strip()) - 1
    except ValueError:
        await message.answer(get_translation(lang, "done_invalid_number"))
        return
    if not (0 <= task_index < len(groups[chat_id]["tasks"])):
        await message.answer(get_translation(lang, "done_invalid_number"))
        return
    task = groups[chat_id]["tasks"][task_index]
    if message.from_user.id != task.get("creator"):
        await message.answer(get_translation(lang, "done_only_creator"))
        return
    confirmations = groups[chat_id]["confirmations"].setdefault(str(task_index), [])
    if message.from_user.id in confirmations:
        await message.answer(get_translation(lang, "done_already_confirmed"))
        return
    else:
        confirmations.append(message.from_user.id)
    if len(set(confirmations)) >= (len(groups[chat_id]["users"]) + 1) // 2:
        groups[chat_id]["tasks"][task_index]["done"] = True
        for user_id in groups[chat_id]["users"]:
            update_user(user_id, "points", get_user(user_id)["points"] + 5)
        await message.answer(get_translation(lang, "done_completed", task=task["task"]))
    else:
        await message.answer(get_translation(lang, "done_waiting"))
    save_groups(groups)

@router.message(Command("edit_task"))
async def edit_group_task_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "edit_task_invalid_number"))
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer(get_translation(lang, "join_group_not_active"))
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(get_translation(lang, "edit_task_usage"))
        return
    try:
        task_index = int(parts[1].strip()) - 1
    except ValueError:
        await message.answer(get_translation(lang, "edit_task_invalid_number"))
        return
    new_text = parts[2].strip()
    if not (3 <= len(new_text) <= 100):
        await message.answer(get_translation(lang, "edit_task_text_length"))
        return
    if not (0 <= task_index < len(groups[chat_id]["tasks"])):
        await message.answer(get_translation(lang, "edit_task_invalid_number"))
        return
    task = groups[chat_id]["tasks"][task_index]
    if message.from_user.id != task.get("creator"):
        await message.answer(get_translation(lang, "edit_task_invalid_number"))
        return
    task["task"] = new_text
    save_groups(groups)
    await message.answer(get_translation(lang, "edit_task_success", num=task_index+1))

@router.message(Command("delete_task"))
async def delete_group_task_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "delete_task_invalid_number"))
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer(get_translation(lang, "join_group_not_active"))
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(get_translation(lang, "delete_task_usage"))
        return
    try:
        task_index = int(parts[1].strip()) - 1
    except ValueError:
        await message.answer(get_translation(lang, "delete_task_invalid_number"))
        return
    if not (0 <= task_index < len(groups[chat_id]["tasks"])):
        await message.answer(get_translation(lang, "delete_task_invalid_number"))
        return
    task = groups[chat_id]["tasks"][task_index]
    if message.from_user.id != task.get("creator"):
        await message.answer(get_translation(lang, "delete_task_not_creator"))
        return
    groups[chat_id]["tasks"].pop(task_index)
    if str(task_index) in groups[chat_id]["confirmations"]:
        del groups[chat_id]["confirmations"][str(task_index)]
    save_groups(groups)
    await message.answer(get_translation(lang, "delete_task_success", num=task_index+1))

@router.message(Command("group_members"))
async def group_members_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "group_members_not_active"))
        return
    if message.from_user.id not in groups[chat_id]["users"]:
        await message.answer(get_translation(lang, "group_members_not_in_group"))
        return

    members = groups[chat_id]["users"]
    if not members:
        await message.answer(get_translation(lang, "group_members_empty"))
        return

    members_text = "\n".join(
        f"{i + 1}. {get_user(member)['name']} " +
        (f"(@{get_user(member)['username']})" if get_user(member).get('username') else "")
        for i, member in enumerate(members)
    )
    await message.answer(f"{get_translation(lang, 'group_members_header')}{members_text}")

@router.message(Command("leave_group"))
async def leave_group_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    groups = get_groups()
    chat_id = str(message.chat.id)
    if chat_id not in groups:
        await message.answer(get_translation(lang, "leave_group_not_active"))
        return

    if message.from_user.id in groups[chat_id]["users"]:
        groups[chat_id]["users"].remove(message.from_user.id)
        save_groups(groups)
        await message.answer(get_translation(lang, "leave_group_success"))
    else:
        await message.answer(get_translation(lang, "leave_group_not_in_group"))