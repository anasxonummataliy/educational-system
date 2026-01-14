import json
import os
from typing import Dict, Any, List
from models import Student, Teacher, Admin

DATA_FILE = "data.json"


def _ensure_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": []}, f)


def load_data() -> Dict[str, Any]:
    _ensure_file()
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data: Dict[str, Any]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def list_users() -> List[Dict[str, Any]]:
    data = load_data()
    return data.get("users", [])


def find_user(username: str):
    users = list_users()
    for u in users:
        if u["username"] == username:
            return u
    return None


def add_user(user_obj):
    data = load_data()
    users = data.get("users", [])
    entry = {
        "username": user_obj.username,
        "password": getattr(user_obj, "_password"),
        "role": user_obj.role,
    }
    if user_obj.role == "Student":
        entry.update(
            {
                "grades": getattr(user_obj, "_grades", {}),
                "attendance": getattr(user_obj, "_attendance", []),
            }
        )
    users.append(entry)
    data["users"] = users
    save_data(data)


def delete_user(username: str) -> bool:
    data = load_data()
    users = data.get("users", [])
    new = [u for u in users if u["username"] != username]
    if len(new) == len(users):
        return False
    data["users"] = new
    save_data(data)
    return True


def update_user(username: str, fields: Dict):
    data = load_data()
    users = data.get("users", [])
    for u in users:
        if u["username"] == username:
            u.update(fields)
            save_data(data)
            return True
    return False


def instantiate_user_from_record(rec: Dict):
    role = rec.get("role")
    if role == "Student":
        s = Student(rec["username"], rec["password"])
        for k, v in rec.get("grades", {}).items():
            s.add_grade(k, v)
        for d in rec.get("attendance", []):
            s.add_attendance(d)
        return s
    if role == "Teacher":
        return Teacher(rec["username"], rec["password"])
    if role == "Admin":
        return Admin(rec["username"], rec["password"])
    return None
