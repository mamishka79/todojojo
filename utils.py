import json
import os
from datetime import datetime

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
REPORTS_FILE = os.path.join(DATA_DIR, "reports.json")

ADMIN_IDS = [1982583714]  # ваш список админов

for file in [USERS_FILE, TASKS_FILE, REPORTS_FILE]:
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)

def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
        except:
            return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user(user_id):
    users = load_json(USERS_FILE)
    return users.get(str(user_id))

def get_user_list():
    """Возвращает список user_id (int)."""
    users = load_json(USERS_FILE)
    return [int(k) for k in users.keys()]

def add_user(user_id, full_name, username):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            "name": full_name,
            "username": username or "",
            "points": 0,
            "completed_tasks": 0,
            "group_access": False,
            "language": "ru",
            "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_json(USERS_FILE, users)
        return True
    else:
        # Если юзер уже есть, обновляем username и дату активности
        existing_username = users[uid].get("username", "")
        if username and existing_username != username:
            users[uid]["username"] = username
        # last_activity тоже стоит обновить
        users[uid]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_json(USERS_FILE, users)
        return False

def update_user(user_id, key, value):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid in users:
        users[uid][key] = value
        # Обновим дату активности при любом изменении
        users[uid]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_json(USERS_FILE, users)

def update_last_activity(user_id):
    """Обновляет поле last_activity у пользователя."""
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid in users:
        users[uid]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_json(USERS_FILE, users)

def add_task(user_id, task_text, status="Новая", deadline=""):
    tasks = load_json(TASKS_FILE)
    uid = str(user_id)
    if uid not in tasks:
        tasks[uid] = []
    tasks[uid].append({
        "task": task_text,
        "done": False,
        "status": status,
        "deadline": deadline
    })
    save_json(TASKS_FILE, tasks)

def get_tasks(user_id):
    tasks_data = load_json(TASKS_FILE)
    uid = str(user_id)
    return tasks_data.get(uid, [])

def complete_task(user_id, task_index):
    tasks_data = load_json(TASKS_FILE)
    uid = str(user_id)
    if uid not in tasks_data:
        return False
    if 0 <= task_index < len(tasks_data[uid]):
        tasks_data[uid][task_index]["done"] = True
        tasks_data[uid][task_index]["status"] = "Завершена"
        save_json(TASKS_FILE, tasks_data)
        return True
    return False

def delete_task(user_id, task_index):
    tasks_data = load_json(TASKS_FILE)
    uid = str(user_id)
    if uid not in tasks_data:
        return False
    if 0 <= task_index < len(tasks_data[uid]):
        # Если задача была выполнена, снимаем 10 очков
        if tasks_data[uid][task_index].get("done"):
            users = load_json(USERS_FILE)
            if uid in users:
                users[uid]["points"] = max(0, users[uid]["points"] - 10)
                users[uid]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_json(USERS_FILE, users)
        tasks_data[uid].pop(task_index)
        save_json(TASKS_FILE, tasks_data)
        return True
    return False

def edit_task(user_id, task_index, new_text):
    tasks_data = load_json(TASKS_FILE)
    uid = str(user_id)
    if uid not in tasks_data:
        return False
    if 0 <= task_index < len(tasks_data[uid]):
        tasks_data[uid][task_index]["task"] = new_text
        save_json(TASKS_FILE, tasks_data)
        return True
    return False

def add_report(reporter_id, reported_id):
    reports = load_json(REPORTS_FILE)
    rep_key = str(reported_id)
    if rep_key not in reports:
        reports[rep_key] = []
    # Если уже жаловался — возвращаем "already_reported"
    if reporter_id in reports[rep_key]:
        return "already_reported"

    # Добавляем жалобу
    reports[rep_key].append(reporter_id)
    save_json(REPORTS_FILE, reports)

    # Если жалоб >= 3, списываем 10 очков
    if len(reports[rep_key]) >= 3:
        users = load_json(USERS_FILE)
        if rep_key in users:
            users[rep_key]["points"] = max(0, users[rep_key]["points"] - 10)
            users[rep_key]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_json(USERS_FILE, users)
        return True
    return False

# ======================================
# Ниже логика проверки дедлайнов

def get_tasks_with_overdue_check(user_id):
    """Возвращает список задач пользователя, попутно проставляя статус 'Просрочена' для невыполненных задач с истёкшим дедлайном."""
    tasks_data = load_json(TASKS_FILE)
    uid = str(user_id)
    if uid not in tasks_data:
        return []
    changed = False
    now = datetime.now()

    for t in tasks_data[uid]:
        if not t.get("done", False):
            # Проверяем дедлайн
            dl = t.get("deadline", "")
            if dl:
                try:
                    # Ожидаем формат 'YYYY-MM-DD HH:MM', к примеру
                    dl_time = datetime.strptime(dl, "%Y-%m-%d %H:%M")
                    # Если дедлайн в прошлом — статус Просрочена
                    if now > dl_time:
                        t["status"] = "Просрочена"
                        changed = True
                except ValueError:
                    pass  # неверный формат, игнорируем

    if changed:
        save_json(TASKS_FILE, tasks_data)
    return tasks_data[uid]
