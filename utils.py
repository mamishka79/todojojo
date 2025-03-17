import json
import os

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
REPORTS_FILE = os.path.join(DATA_DIR, "reports.json")

for file in [USERS_FILE, TASKS_FILE, REPORTS_FILE]:
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_user(user_id):
    users = load_json(USERS_FILE)
    return users.get(str(user_id), None)

def add_user(user_id, full_name, username):
    users = load_json(USERS_FILE)
    user_id_str = str(user_id)

    if user_id_str not in users:
        users[user_id_str] = {
            "name": full_name,
            "username": username or "",
            "points": 0,
            "completed_tasks": 0,
            "group_access": False,
            "language": "ru"  # добавлено поле языка с дефолтным значением "ru"
        }
        save_json(USERS_FILE, users)
        return True
    else:
        existing_username = users[user_id_str].get("username", "")
        if username and existing_username != username:
            users[user_id_str]["username"] = username
            save_json(USERS_FILE, users)
        return False

def update_user(user_id, key, value):
    users = load_json(USERS_FILE)
    if str(user_id) in users:
        users[str(user_id)][key] = value
        save_json(USERS_FILE, users)

def add_task(user_id, task_text):
    tasks = load_json(TASKS_FILE)
    tasks.setdefault(str(user_id), []).append({"task": task_text, "done": False})
    save_json(TASKS_FILE, tasks)

def get_tasks(user_id):
    tasks = load_json(TASKS_FILE)
    return tasks.get(str(user_id), [])

def complete_task(user_id, task_index):
    tasks = load_json(TASKS_FILE)
    if str(user_id) in tasks and 0 <= task_index < len(tasks[str(user_id)]):
        tasks[str(user_id)][task_index]["done"] = True
        save_json(TASKS_FILE, tasks)
        return True
    return False

def delete_task(user_id, task_index):
    tasks = load_json(TASKS_FILE)
    if str(user_id) in tasks and 0 <= task_index < len(tasks[str(user_id)]):
        if tasks[str(user_id)][task_index]["done"]:
            users = load_json(USERS_FILE)
            if str(user_id) in users:
                users[str(user_id)]["points"] = max(0, users[str(user_id)]["points"] - 10)
                save_json(USERS_FILE, users)
        tasks[str(user_id)].pop(task_index)
        save_json(TASKS_FILE, tasks)
        return True
    return False

def edit_task(user_id, task_index, new_text):
    tasks = load_json(TASKS_FILE)
    if str(user_id) in tasks and 0 <= task_index < len(tasks[str(user_id)]):
        tasks[str(user_id)][task_index]["task"] = new_text
        save_json(TASKS_FILE, tasks)
        return True
    return False

def add_report(reporter_id, reported_id):
    reports = load_json(REPORTS_FILE)
    rep_key = str(reported_id)
    reports.setdefault(rep_key, [])
    # Если пользователь уже пожаловался – возвращаем специальное значение
    if reporter_id in reports[rep_key]:
        return "already_reported"
    reports[rep_key].append(reporter_id)
    save_json(REPORTS_FILE, reports)

    if len(reports[rep_key]) >= 3:
        users = load_json(USERS_FILE)
        if rep_key in users:
            users[rep_key]["points"] = max(0, users[rep_key]["points"] - 10)
            save_json(USERS_FILE, users)
        return True
    return False