import json
import os

DATA_FILE = "university_data.json"


def save_data(users):
    with open(DATA_FILE, "w") as f:
        json.dump([u.to_dict() for u in users], f, indent=4)


def load_data():
    from models import Student, Teacher, Admin

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        users = []
        for item in data:
            if item["role"] == "Student":
                users.append(
                    Student(
                        item["user_id"],
                        item["name"],
                        item["password"],
                        item.get("grades"),
                        item.get("attendance"),
                    )
                )
            elif item["role"] == "Teacher":
                users.append(Teacher(item["user_id"], item["name"], item["password"]))
            elif item["role"] == "Admin":
                users.append(Admin(item["user_id"], item["name"], item["password"]))
        return users
