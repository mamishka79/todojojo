from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from utils import add_user, load_json

class TaskState(StatesGroup):
    add = State()
    complete = State()
    delete = State()
    edit_index = State()
    edit_text = State()

router = Router()

solo_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Добавить задачу"), KeyboardButton(text="📋 Мои задачи")],
    [KeyboardButton(text="✅ Завершить задачу"), KeyboardButton(text="🗑 Удалить задачу")],
    [KeyboardButton(text="✏️ Редактировать задачу"), KeyboardButton(text="🏆 Рейтинг")]
], resize_keyboard=True)

@router.message(F.text == "/help")
async def help_cmd(message: Message):
    help_text = (
        "Инструкции для бота в Solo режиме:\n\n"
        "/start - регистрация бота\n"
        "➕ Добавить задачу – добавить новую задачу\n"
        "📋 Мои задачи – показать список твоих задач\n"
        "✅ Завершить задачу – отметить задачу как выполненную и получить +10 очков\n"
        "🗑 Удалить задачу – удалить задачу\n"
        "✏️ Редактировать задачу – изменить текст задачи\n"
        "🏆 Рейтинг – посмотреть рейтинг пользователей\n"
        "/help – показать эту справку"
    )
    await message.answer(help_text)

@router.message(F.text == "🏆 Рейтинг")
async def leaderboard_cmd(message: Message):
    users = load_json("data/users.json")
    sorted_users = sorted(users.items(), key=lambda x: x[1]["points"], reverse=True)

    text = "\n".join(
        f"{i+1}. {user_data['name']} "
        f"{f'(@{user_data['username']}) ' if user_data.get('username') else ''}"
        f"– {user_data['points']} очков "
        f"{'(групповая версия)' if user_data.get('group_access') else '(solo)'}"
        for i, (_, user_data) in enumerate(sorted_users)
    )

    await message.answer(f"🏆 Рейтинг пользователей:\n{text}")

@router.message(F.text == "/start")
async def start_cmd(message: Message):
    username = message.from_user.username

    if add_user(message.from_user.id, message.from_user.full_name, username):
        await message.answer("👋 Привет! Ты зарегистрирован.", reply_markup=solo_kb)
    else:
        await message.answer("Ты уже зарегистрирован!", reply_markup=solo_kb)

@router.message(F.text == "➕ Добавить задачу")
async def add_task_cmd(message: Message, state: FSMContext):
    await message.answer("Отправь мне текст задачи.")
    await state.set_state(TaskState.add)

@router.message(TaskState.add)
async def process_add_task(message: Message, state: FSMContext):
    task_text = message.text.strip()
    if not (3 <= len(task_text) <= 100):
        await message.answer("Текст задачи должен быть от 3 до 100 символов. Попробуй снова.")
        return

    from utils import add_task
    add_task(message.from_user.id, task_text)
    await message.answer("✅ Задача добавлена!")
    await state.clear()

@router.message(F.text == "📋 Мои задачи")
async def my_tasks(message: Message):
    user_id = str(message.from_user.id)
    tasks = load_json("data/tasks.json")

    if user_id not in tasks or not tasks[user_id]:
        await message.answer("ℹ️ У тебя пока нет задач.")
        return

    task_list = "\n".join([
        f"{idx + 1}. {'✅' if task['done'] else '❌'} {task['task']}"
        for idx, task in enumerate(tasks[user_id])
    ])
    await message.answer(f"📋 *Твои задачи:*\n\n{task_list}", parse_mode="Markdown")

@router.message(F.text == "✅ Завершить задачу")
async def done_task_cmd(message: Message, state: FSMContext):
    await message.answer("Напиши номер задачи, которую ты выполнил.")
    await state.set_state(TaskState.complete)

@router.message(TaskState.complete, F.text.regexp(r"^\d+$"))
async def complete_task_cmd(message: Message, state: FSMContext):
    from utils import complete_task, get_user, update_user
    task_index = int(message.text) - 1
    if complete_task(message.from_user.id, task_index):
        user_data = get_user(message.from_user.id)
        update_user(message.from_user.id, "points", user_data["points"] + 10)
        await message.answer("✅ Задача завершена! +10 очков!")
    else:
        await message.answer("⚠️ Ошибка! Проверь номер задачи.")
    await state.clear()

@router.message(F.text == "🗑 Удалить задачу")
async def delete_task_prompt(message: Message, state: FSMContext):
    await message.answer("Напиши номер задачи, которую хочешь удалить.")
    await state.set_state(TaskState.delete)

@router.message(TaskState.delete, F.text.regexp(r"^\d+$"))
async def delete_task_cmd(message: Message, state: FSMContext):
    from utils import delete_task
    task_index = int(message.text) - 1
    if delete_task(message.from_user.id, task_index):
        await message.answer("✅ Задача удалена!")
    else:
        await message.answer("⚠️ Ошибка! Проверь номер задачи.")
    await state.clear()


@router.message(F.text == "✏️ Редактировать задачу")
async def edit_task_cmd(message: Message, state: FSMContext):
    await message.answer("Напиши номер задачи, которую хочешь отредактировать.")
    await state.set_state(TaskState.edit_index)


@router.message(TaskState.edit_index, F.text.regexp(r"^\d+$"))
async def get_task_index_for_edit(message: Message, state: FSMContext):
    task_index = int(message.text) - 1
    await state.update_data(task_index=task_index)

    await message.answer("Теперь напиши новый текст задачи.")
    await state.set_state(TaskState.edit_text)


@router.message(TaskState.edit_text)
async def edit_task_text(message: Message, state: FSMContext):
    from utils import edit_task
    data = await state.get_data()
    task_index = data.get("task_index")
    new_text = message.text.strip()

    if edit_task(message.from_user.id, task_index, new_text):
        await message.answer("✅ Задача успешно отредактирована!")
    else:
        await message.answer("⚠️ Ошибка при редактировании. Проверь номер задачи.")

    await state.clear()