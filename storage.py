import json
import os
from typing import Dict, Any, List
from models import Student, Teacher, Admin, Subject

DATA_FILE = "data.json"


def _ensure_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": [], "subjects": []}, f)


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


def list_subjects() -> List[Dict[str, Any]]:
    data = load_data()
    return data.get("subjects", [])


def find_user(username: str):
    users = list_users()
    for u in users:
        if u["username"] == username:
            return u
    return None


def find_subject(code: str):
    subjects = list_subjects()
    for s in subjects:
        if s["code"] == code:
            return s
    return None


def add_user(user_obj):
    data = load_data()
    users = data.get("users", [])
    entry = {
        "username": user_obj.username,
        "password": getattr(user_obj, "_password"),
        "role": user_obj.role,
    }

    if user_obj.role == "Teacher":
        entry["subjects"] = getattr(user_obj, "subjects", [])
    elif user_obj.role == "Student":
        entry["grades"] = getattr(user_obj, "_grades", {})
        entry["attendance"] = getattr(user_obj, "_attendance", {})

    users.append(entry)
    data["users"] = users
    save_data(data)


def add_subject(subject: Subject):
    data = load_data()
    subjects = data.get("subjects", [])
    subjects.append(subject.to_dict())
    data["subjects"] = subjects
    save_data(data)


def update_subject(code: str, fields: Dict):
    data = load_data()
    subjects = data.get("subjects", [])
    for s in subjects:
        if s["code"] == code:
            s.update(fields)
            save_data(data)
            return True
    return False


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


def _normalize_grades(grades_data):
    if not grades_data:
        return {}

    if isinstance(grades_data, dict):
        normalized = {}
        for key, value in grades_data.items():
            if isinstance(value, dict):
                normalized[key] = value
            elif isinstance(value, (int, float)):
                if key not in normalized:
                    normalized["GENERAL"] = {}
                normalized["GENERAL"][
                    f"task_{len(normalized.get('GENERAL', {}))}"
                ] = value
        return normalized
    return {}


def _normalize_attendance(attendance_data):
    if not attendance_data:
        return {}

    if isinstance(attendance_data, dict):
        normalized = {}
        for key, value in attendance_data.items():
            if isinstance(value, list):
                normalized[key] = value
        return normalized
    elif isinstance(attendance_data, list):
        return {"GENERAL": attendance_data}
    return {}


def instantiate_user_from_record(rec: Dict):
    role = rec.get("role", "").capitalize()

    if role == "Student":
        s = Student(rec["username"], rec["password"])
        s._grades = _normalize_grades(rec.get("grades", {}))
        s._attendance = _normalize_attendance(rec.get("attendance", {}))
        return s
    elif role == "Teacher":
        t = Teacher(rec["username"], rec["password"])
        t.subjects = rec.get("subjects", [])
        return t
    elif role == "Admin":
        return Admin(rec["username"], rec["password"])
    return None
