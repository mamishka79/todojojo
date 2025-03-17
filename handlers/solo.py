from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from utils import add_user, load_json, get_user, add_task, complete_task, update_user, delete_task, edit_task

router = Router()

# Функция для генерации клавиатуры в зависимости от выбранного языка
def get_solo_keyboard(lang="ru"):
    if lang == "en":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Add Task"), KeyboardButton(text="📋 My Tasks")],
                [KeyboardButton(text="✅ Complete Task"), KeyboardButton(text="🗑 Delete Task")],
                [KeyboardButton(text="✏️ Edit Task"), KeyboardButton(text="🏆 Leaderboard")],
                [KeyboardButton(text="🌐 Language")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Добавить задачу"), KeyboardButton(text="📋 Мои задачи")],
                [KeyboardButton(text="✅ Завершить задачу"), KeyboardButton(text="🗑 Удалить задачу")],
                [KeyboardButton(text="✏️ Редактировать задачу"), KeyboardButton(text="🏆 Рейтинг")],
                [KeyboardButton(text="🌐 Язык")]
            ],
            resize_keyboard=True
        )

# Функция перевода – возвращает строку для заданного ключа и языка
def get_translation(lang, key):
    translations = {
        "welcome_message": {
            "ru": "Привет! Добро пожаловать в наш бот для управления задачами.",
            "en": "Hello! Welcome to our task management bot."
        },
        "instruction_message": {
            "ru": (
                "Чтобы начать, добавь новую задачу, нажав кнопку '➕ Добавить задачу'.\n\n"
                "Ты можешь отправлять задачи списком, разделяя их символом ';'. Например:\n"
                "Купить хлеб; Позвонить маме; Сделать домашнее задание\n\n"
                "Затем ты сможешь просматривать свои задачи, отмечать их как выполненные и получать очки."
            ),
            "en": (
                "To get started, add a new task by pressing the '➕ Add Task' button.\n\n"
                "You can also send multiple tasks in one message, separated by a semicolon ';'. For example:\n"
                "Buy bread; Call mom; Do homework\n\n"
                "Then you'll be able to view your tasks, mark them as completed, and earn points."
            )
        },
        "next_steps_message": {
            "ru": (
                "Дополнительно, вот еще несколько возможностей:\n"
                "- Нажми '📋 Мои задачи' для просмотра списка задач (они разделены на невыполненные и выполненные).\n"
                "- Нажми '✅ Завершить задачу', чтобы отметить задачу как выполненную и получить +10 очков.\n"
                "- Нажми '✏️ Редактировать задачу' или '🗑 Удалить задачу' для изменения или удаления задачи.\n\n"
                "Для группового режима: чтобы активировать его, необходимо набрать 120 очков и воспользоваться командой /start_group. "
                "Групповой режим позволяет работать совместно с друзьями: добавлять групповые задачи, просматривать участников, подтверждать выполнение и т.д.\n\n"
                "Если потребуется помощь, нажми /help."
            ),
            "en": (
                "Additionally, here are some extra features:\n"
                "- Press '📋 My Tasks' to view your tasks (they are separated into incomplete and completed).\n"
                "- Press '✅ Complete Task' to mark a task as completed and earn +10 points.\n"
                "- Use '✏️ Edit Task' or '🗑 Delete Task' to modify or delete a task.\n\n"
                "For group mode: To activate it, you need to accumulate 120 points and use the /start_group command. "
                "Group mode lets you work together with friends: add group tasks, view members, confirm task completion, etc.\n\n"
                "If you need help, type /help."
            )
        },
        "start_registered": {
            "ru": "👋 Ты успешно зарегистрирован.",
            "en": "👋 You have successfully registered."
        },
        "already_registered": {
            "ru": "Ты уже зарегистрирован!",
            "en": "You are already registered!"
        },
        "help": {
            "ru": (
                "Инструкции для бота в Solo режиме:\n\n"
                "Команды:\n"
                "  /start — регистрация бота и вывод подробной инструкции.\n"
                "  ➕ Добавить задачу — добавить новую задачу. Ты можешь отправлять сразу несколько задач, разделяя их символом ';'.\n"
                "  📋 Мои задачи — показать список твоих задач, разделённых на не выполненные и выполненные.\n"
                "  ✅ Завершить задачу — отметить задачу как выполненную и получить +10 очков.\n"
                "  🗑 Удалить задачу — удалить задачу по её номеру.\n"
                "  ✏️ Редактировать задачу — изменить текст задачи, указав её номер.\n"
                "  🏆 Рейтинг — посмотреть рейтинг пользователей.\n"
                "  🌐 Язык — изменить язык интерфейса.\n\n"
                "Групповой режим:\n"
                "  Для активации группового режима необходимо набрать не менее 120 очков и ввести команду /start_group.\n"
                "  В групповой версии доступны команды для присоединения к группе, добавления, редактирования и удаления групповых задач,\n"
                "  а также подтверждение выполнения задач участниками группы.\n\n"
                "Дополнительные возможности:\n"
                "- Отправляй список задач в одном сообщении, разделяя задачи символом ';'.\n"
                "- Команды работают как на русском, так и на английском языке."
            ),
            "en": (
                "Instructions for the bot in Solo mode:\n\n"
                "Commands:\n"
                "  /start — register with the bot and display detailed instructions.\n"
                "  ➕ Add Task — add a new task. You can send multiple tasks in one message separated by ';'.\n"
                "  📋 My Tasks — view your tasks, separated into incomplete and completed tasks.\n"
                "  ✅ Complete Task — mark a task as completed and earn +10 points.\n"
                "  🗑 Delete Task — delete a task by its number.\n"
                "  ✏️ Edit Task — modify a task by specifying its number.\n"
                "  🏆 Leaderboard — view the user rankings.\n"
                "  🌐 Language — change the interface language.\n\n"
                "Group mode:\n"
                "  To activate group mode, you need to accumulate at least 120 points and use the /start_group command.\n"
                "  In group mode, you can join a group, add, edit, or delete group tasks, and confirm task completion by group members.\n\n"
                "Additional features:\n"
                "- You can send a list of tasks in one message, separating them with ';'.\n"
                "- All commands work in both Russian and English."
            )
        },
        "ask_task_text": {
            "ru": "Отправь мне текст задачи.",
            "en": "Send me the task text."
        },
        "task_length_error": {
            "ru": "Текст задачи должен быть от 3 до 100 символов. Попробуй снова.",
            "en": "Task text must be between 3 and 100 characters. Please try again."
        },
        "task_added": {
            "ru": "✅ Задача добавлена!",
            "en": "✅ Task added!"
        },
        "no_tasks": {
            "ru": "ℹ️ У тебя пока нет задач.",
            "en": "ℹ️ You have no tasks yet."
        },
        "your_tasks": {
            "ru": "📋 *Твои задачи:*\n",
            "en": "📋 *Your Tasks:*\n"
        },
        "ask_task_number_complete": {
            "ru": "Напиши номер задачи, которую ты выполнил.",
            "en": "Enter the number of the task you completed."
        },
        "task_completed": {
            "ru": "✅ Задача завершена! +10 очков!",
            "en": "✅ Task completed! +10 points!"
        },
        "error_task_number": {
            "ru": "⚠️ Ошибка! Проверь номер задачи.",
            "en": "⚠️ Error! Check the task number."
        },
        "ask_task_number_delete": {
            "ru": "Напиши номер задачи, которую хочешь удалить.",
            "en": "Enter the number of the task you want to delete."
        },
        "task_deleted": {
            "ru": "✅ Задача удалена!",
            "en": "✅ Task deleted!"
        },
        "ask_task_number_edit": {
            "ru": "Напиши номер задачи, которую хочешь отредактировать.",
            "en": "Enter the number of the task you want to edit."
        },
        "ask_new_task_text": {
            "ru": "Теперь напиши новый текст задачи.",
            "en": "Now, enter the new task text."
        },
        "task_edited": {
            "ru": "✅ Задача успешно отредактирована!",
            "en": "✅ Task successfully edited!"
        },
        "error_editing": {
            "ru": "⚠️ Ошибка при редактировании. Проверь номер задачи.",
            "en": "⚠️ Error editing task. Check the task number."
        }
    }
    return translations.get(key, {}).get(lang, translations.get(key, {}).get("ru", ""))

class TaskState(StatesGroup):
    add = State()
    complete = State()
    delete = State()
    edit_index = State()
    edit_text = State()

@router.message(F.text.in_(["/help"]))
async def help_cmd(message: Message):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    help_text = get_translation(lang, "help")
    await message.answer(help_text)

@router.message(F.text.in_(["/start"]))
async def start_cmd(message: Message):
    username = message.from_user.username
    user_created = add_user(message.from_user.id, message.from_user.full_name, username)
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    solo_kb = get_solo_keyboard(lang)
    if user_created:
        # Отправляем последовательные инструкции
        await message.answer(get_translation(lang, "welcome_message"), reply_markup=solo_kb)
        await message.answer(get_translation(lang, "instruction_message"))
        await message.answer(get_translation(lang, "next_steps_message"))
    else:
        await message.answer(get_translation(lang, "already_registered"), reply_markup=solo_kb)

@router.message(F.text.in_(["➕ Добавить задачу", "➕ Add Task"]))
async def add_task_cmd(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    await message.answer(get_translation(lang, "ask_task_text"))
    await state.set_state(TaskState.add)

@router.message(TaskState.add)
async def process_add_task(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    task_text = message.text.strip()
    # Если пользователь отправляет список задач, разделенных символом ';'
    if ";" in task_text:
        tasks_list = [t.strip() for t in task_text.split(";") if t.strip()]
        added = []
        for t in tasks_list:
            if 3 <= len(t) <= 100:
                add_task(message.from_user.id, t)
                added.append(t)
        if added:
            await message.answer("✅ Добавлены задачи: " + ", ".join(added))
        else:
            await message.answer(get_translation(lang, "task_length_error"))
        await state.clear()
        return

    if not (3 <= len(task_text) <= 100):
        await message.answer(get_translation(lang, "task_length_error"))
        return

    add_task(message.from_user.id, task_text)
    await message.answer(get_translation(lang, "task_added"))
    await state.clear()

@router.message(F.text.in_(["📋 Мои задачи", "📋 My Tasks"]))
async def my_tasks(message: Message):
    user_id = str(message.from_user.id)
    tasks = load_json("data/tasks.json")
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"

    if user_id not in tasks or not tasks[user_id]:
        await message.answer(get_translation(lang, "no_tasks"))
        return

    incomplete_tasks = []
    completed_tasks = []
    for i, task in enumerate(tasks[user_id]):
        if task.get("done"):
            completed_tasks.append((i, task))
        else:
            incomplete_tasks.append((i, task))
    display_text = ""
    if incomplete_tasks:
        if lang == "en":
            display_text += "❌ Incomplete Tasks:\n"
        else:
            display_text += "❌ Не выполненные задачи:\n"
        for idx, task in incomplete_tasks:
            display_text += f"{idx+1}. {task['task']}\n"
    if completed_tasks:
        display_text += "\n"
        if lang == "en":
            display_text += "✅ Completed Tasks:\n"
        else:
            display_text += "✅ Выполненные задачи:\n"
        for idx, task in completed_tasks:
            display_text += f"{idx+1}. {task['task']}\n"

    await message.answer(f"{get_translation(lang, 'your_tasks')}\n{display_text}", parse_mode="Markdown")

@router.message(F.text.in_(["✅ Завершить задачу", "✅ Complete Task"]))
async def done_task_cmd(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    await message.answer(get_translation(lang, "ask_task_number_complete"))
    await state.set_state(TaskState.complete)

@router.message(TaskState.complete, F.text.regexp(r"^\d+$"))
async def complete_task_cmd(message: Message, state: FSMContext):
    from utils import complete_task, get_user, update_user
    task_index = int(message.text) - 1
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    if complete_task(message.from_user.id, task_index):
        user_data = get_user(message.from_user.id)
        update_user(message.from_user.id, "points", user_data["points"] + 10)
        await message.answer(get_translation(lang, "task_completed"))
    else:
        await message.answer(get_translation(lang, "error_task_number"))
    await state.clear()

@router.message(F.text.in_(["🗑 Удалить задачу", "🗑 Delete Task"]))
async def delete_task_prompt(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    await message.answer(get_translation(lang, "ask_task_number_delete"))
    await state.set_state(TaskState.delete)

@router.message(TaskState.delete, F.text.regexp(r"^\d+$"))
async def delete_task_cmd(message: Message, state: FSMContext):
    from utils import delete_task
    task_index = int(message.text) - 1
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    if delete_task(message.from_user.id, task_index):
        await message.answer(get_translation(lang, "task_deleted"))
    else:
        await message.answer(get_translation(lang, "error_task_number"))
    await state.clear()

@router.message(F.text.in_(["✏️ Редактировать задачу", "✏️ Edit Task"]))
async def edit_task_cmd(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    await message.answer(get_translation(lang, "ask_task_number_edit"))
    await state.set_state(TaskState.edit_index)

@router.message(TaskState.edit_index, F.text.regexp(r"^\d+$"))
async def get_task_index_for_edit(message: Message, state: FSMContext):
    task_index = int(message.text) - 1
    await state.update_data(task_index=task_index)
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"
    await message.answer(get_translation(lang, "ask_new_task_text"))
    await state.set_state(TaskState.edit_text)

@router.message(TaskState.edit_text)
async def edit_task_text(message: Message, state: FSMContext):
    from utils import edit_task
    data = await state.get_data()
    task_index = data.get("task_index")
    new_text = message.text.strip()
    user = get_user(message.from_user.id)
    lang = user.get("language", "ru") if user else "ru"

    if edit_task(message.from_user.id, task_index, new_text):
        await message.answer(get_translation(lang, "task_edited"))
    else:
        await message.answer(get_translation(lang, "error_editing"))
    await state.clear()
