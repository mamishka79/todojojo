from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from utils import (
    add_user, load_json, get_user, add_task, complete_task, update_user,
    delete_task, edit_task, update_last_activity, get_tasks_with_overdue_check
)

router = Router()

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

def get_translation(lang, key):
    translations = {
        "welcome_message": {
            "ru": "Привет! Добро пожаловать в наш бот для управления задачами.",
            "en": "Hello! Welcome to our task management bot."
        },
        "instruction_message": {
            "ru": (
                "Чтобы начать, добавь новую задачу, нажав кнопку '➕ Добавить задачу'.\n\n"
                "Ты можешь отправлять задачи списком, разделяя их либо переносами строк, либо символом ';'.\n"
                "Например:\nКупить хлеб\nПозвонить маме;Сделать домашнее задание\n\n"
                "Затем ты сможешь просматривать свои задачи, отмечать их как выполненные и получать очки."
            ),
            "en": (
                "To get started, add a new task by pressing the '➕ Add Task' button.\n\n"
                "You can also send multiple tasks in one message, separated by new lines or a semicolon ';'.\n"
                "For example:\nBuy bread\nCall mom;Do homework\n\n"
                "Then you'll be able to view your tasks, mark them as completed, and earn points."
            )
        },
        "next_steps_message": {
            "ru": (
                "Дополнительно, вот еще несколько возможностей:\n"
                "- '📋 Мои задачи' для просмотра списка задач (невыполненные и выполненные).\n"
                "- '✅ Завершить задачу' для +10 очков.\n"
                "- '✏️ Редактировать задачу' или '🗑 Удалить задачу'.\n\n"
                "Для группового режима: набери 120 очков и /start_group.\n"
                "Групповой режим: совместное добавление/редактирование задач с друзьями.\n\n"
                "Если нужна помощь — /help."
            ),
            "en": (
                "Additionally, here are some features:\n"
                "- '📋 My Tasks' to see incomplete and completed tasks.\n"
                "- '✅ Complete Task' to earn +10 points.\n"
                "- '✏️ Edit Task' or '🗑 Delete Task' to modify or remove tasks.\n\n"
                "For group mode: accumulate 120 points and use /start_group.\n"
                "Group mode: collaborate with friends.\n\n"
                "If you need help — type /help."
            )
        },
        "already_registered": {
            "ru": "Ты уже зарегистрирован!",
            "en": "You are already registered!"
        },
        "ask_task_text": {
            "ru": "Отправь мне задачи (каждую на новой строке или через ';').",
            "en": "Send your tasks (each on a new line or separated by ';')."
        },
        "task_length_error": {
            "ru": "Текст задачи должен быть от 3 до 100 символов. Попробуй снова.",
            "en": "Task text must be 3–100 characters. Please try again."
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
            "en": "Enter the task number you completed."
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
            "en": "Enter the task number you want to delete."
        },
        "task_deleted": {
            "ru": "✅ Задача удалена!",
            "en": "✅ Task deleted!"
        },
        "ask_task_number_edit": {
            "ru": "Напиши номер задачи, которую хочешь отредактировать.",
            "en": "Enter the task number you want to edit."
        },
        "ask_new_task_text": {
            "ru": "Теперь напиши новый текст задачи.",
            "en": "Now enter the new task text."
        },
        "task_edited": {
            "ru": "✅ Задача успешно отредактирована!",
            "en": "✅ Task successfully edited!"
        },
        "error_editing": {
            "ru": "⚠️ Ошибка при редактировании. Проверь номер задачи.",
            "en": "⚠️ Error editing. Check the task number."
        },
        "welcome_message": {
            "ru": "Привет! Добро пожаловать в наш бот для управления задачами.",
            "en": "Hello! Welcome to our task management bot."
        },
        "instruction_message": {
            "ru": "Здесь могли быть более детальные инструкции, но уже всё понятно 😉",
            "en": "Here could be more instructions, but it's quite straightforward 😉"
        }
    }
    return translations.get(key, {}).get(lang, "")

class TaskState(StatesGroup):
    add = State()
    complete = State()
    delete = State()
    edit_index = State()
    edit_text = State()

@router.message(F.text.in_(["/help"]))
async def help_cmd(message: Message):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"] if user else "ru"
    await message.answer(get_translation(lang, "instruction_message"))

@router.message(F.text.in_(["/start"]))
async def start_cmd(message: Message):
    user_created = add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"]
    solo_kb = get_solo_keyboard(lang)

    if user_created:
        await message.answer(get_translation(lang, "welcome_message"), reply_markup=solo_kb)
        await message.answer(get_translation(lang, "instruction_message"))
        await message.answer(get_translation(lang, "next_steps_message"))
    else:
        await message.answer(get_translation(lang, "already_registered"), reply_markup=solo_kb)

@router.message(F.text.in_(["➕ Добавить задачу", "➕ Add Task"]))
async def add_task_cmd(message: Message, state: FSMContext):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"] if user else "ru"
    await message.answer(get_translation(lang, "ask_task_text"))
    await state.set_state(TaskState.add)

@router.message(TaskState.add)
async def process_add_task(message: Message, state: FSMContext):
    # Обновим активность
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"] if user else "ru"

    raw = message.text.strip()
    # Разделяем вход на строки (или на ; )
    # так же, как было раньше
    lines = []
    for line in raw.split('\n'):
        if ';' in line:
            for part in line.split(';'):
                t = part.strip()
                if t:
                    lines.append(t)
        else:
            if line.strip():
                lines.append(line.strip())

    # Если после всех разделений нет строк – ошибка
    if not lines:
        await message.answer(get_translation(lang, "task_length_error"))
        return

    added_tasks = []
    for line in lines:
        # Попробуем распарсить 3 части: 
        #   text | deadline | status
        parts = [p.strip() for p in line.split('|')]
        
        # Минимум 1 часть (текст)
        text = parts[0] if len(parts) >= 1 else ""
        deadline = parts[1] if len(parts) >= 2 else ""
        status = parts[2] if len(parts) >= 3 else ""

        # Если нет текста или текст слишком короткий - пропускаем
        if len(text) < 3 or len(text) > 100:
            continue
        
        # Установим статус по умолчанию, если не задан
        if not status:
            status = "Новая" if lang == "ru" else "New"

        # Проверим формат дедлайна (если пользователь ввёл)
        # Не обязательно, но полезно
        if deadline:
            from datetime import datetime
            try:
                datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                # Если формат корректен, просто используем его
            except ValueError:
                # Если формат некорректен, можно проигнорировать дедлайн 
                # или сказать пользователю, что дедлайн неверен
                deadline = ""

        # Теперь добавим задачу
        add_task(
            user_id=message.from_user.id,
            task_text=text,
            status=status,
            deadline=deadline
        )
        added_tasks.append(text)

    # После цикла, проверим сколько добавлено
    if added_tasks:
        if len(added_tasks) == 1:
            # Если ровно одна
            await message.answer(get_translation(lang, "task_added"))
        else:
            # Если несколько
            joined = ", ".join(added_tasks[:5])
            await message.answer(f"✅ Добавлено задач: {len(added_tasks)}. Пример: {joined}")
    else:
        # Если в итоге ни одной задачи не прошло валидацию
        await message.answer(get_translation(lang, "task_length_error"))

    # Сбросим состояние
    await state.clear()

@router.message(F.text.in_(["📋 Мои задачи", "📋 My Tasks"]))
async def my_tasks(message: Message):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"] if user else "ru"

    tasks = get_tasks_with_overdue_check(message.from_user.id)
    if not tasks:
        await message.answer(get_translation(lang, "no_tasks"))
        return

    incomplete_tasks = []
    completed_tasks = []
    for i, task in enumerate(tasks):
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
            st = task.get("status", "Новая")
            dl = task.get("deadline", "")
            display_text += f"{idx+1}. {task['task']} [{st}]"
            if dl:
                display_text += f" (deadline: {dl})"
            display_text += "\n"

    if completed_tasks:
        display_text += "\n"
        if lang == "en":
            display_text += "✅ Completed Tasks:\n"
        else:
            display_text += "✅ Выполненные задачи:\n"
        for idx, task in completed_tasks:
            st = task.get("status", "Завершена")
            dl = task.get("deadline", "")
            display_text += f"{idx+1}. {task['task']} [{st}]"
            if dl:
                display_text += f" (deadline: {dl})"
            display_text += "\n"

    await message.answer(f"{get_translation(lang, 'your_tasks')}{display_text}", parse_mode="Markdown")

@router.message(F.text.in_(["✅ Завершить задачу", "✅ Complete Task"]))
async def done_task_cmd(message: Message, state: FSMContext):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"]
    await message.answer(get_translation(lang, "ask_task_number_complete"))
    await state.set_state(TaskState.complete)

@router.message(TaskState.complete, F.text.regexp(r"^\d+$"))
async def complete_task_cmd(message: Message, state: FSMContext):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"]
    idx = int(message.text) - 1

    if complete_task(message.from_user.id, idx):
        user_data = get_user(message.from_user.id)
        update_user(message.from_user.id, "points", user_data["points"] + 10)
        await message.answer(get_translation(lang, "task_completed"))
    else:
        await message.answer(get_translation(lang, "error_task_number"))
    await state.clear()

@router.message(F.text.in_(["🗑 Удалить задачу", "🗑 Delete Task"]))
async def delete_task_prompt(message: Message, state: FSMContext):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"]
    await message.answer(get_translation(lang, "ask_task_number_delete"))
    await state.set_state(TaskState.delete)

@router.message(TaskState.delete, F.text.regexp(r"^\d+$"))
async def delete_task_cmd_handler(message: Message, state: FSMContext):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"]
    idx = int(message.text) - 1

    if delete_task(message.from_user.id, idx):
        await message.answer(get_translation(lang, "task_deleted"))
    else:
        await message.answer(get_translation(lang, "error_task_number"))
    await state.clear()

@router.message(F.text.in_(["✏️ Редактировать задачу", "✏️ Edit Task"]))
async def edit_task_cmd(message: Message, state: FSMContext):
    update_last_activity(message.from_user.id)
    user = get_user(message.from_user.id)
    lang = user["language"]
    await message.answer(get_translation(lang, "ask_task_number_edit"))
    await state.set_state(TaskState.edit_index)

@router.message(TaskState.edit_index, F.text.regexp(r"^\d+$"))
async def get_task_index_for_edit(message: Message, state: FSMContext):
    update_last_activity(message.from_user.id)
    idx = int(message.text) - 1
    await state.update_data(task_index=idx)
    user = get_user(message.from_user.id)
    lang = user["language"]
    await message.answer(get_translation(lang, "ask_new_task_text"))
    await state.set_state(TaskState.edit_text)

@router.message(TaskState.edit_text)
async def edit_task_text_handler(message: Message, state: FSMContext):
    update_last_activity(message.from_user.id)
    data = await state.get_data()
    idx = data.get("task_index")
    new_text = message.text.strip()
    user = get_user(message.from_user.id)
    lang = user["language"]

    if edit_task(message.from_user.id, idx, new_text):
        await message.answer(get_translation(lang, "task_edited"))
    else:
        await message.answer(get_translation(lang, "error_editing"))
    await state.clear()
