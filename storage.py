import json
from pathlib import Path
from typing import Dict
from models import Admin, Teacher, Student


class Storage:
    def __init__(self, base_dir: str | Path = None):
        self.base = Path(base_dir or Path.cwd()) / "data"
        self.base.mkdir(parents=True, exist_ok=True)
        self.users_file = self.base / "users.json"
        if not self.users_file.exists():
            # bootstrap default admin
            admin = {"type": "admin", "username": "admin", "password": "admin"}
            self._write([admin])

    def _read(self):
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write(self, data):
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def list_users(self) -> Dict[str, object]:
        raw = self._read()
        res = {}
        for u in raw:
            t = u.get("type")
            if t == "admin":
                res[u["username"]] = Admin(u["username"], u.get("password", ""))
            elif t == "teacher":
                res[u["username"]] = Teacher(u["username"], u.get("password", ""))
            elif t == "student":
                res[u["username"]] = Student.from_dict(u)
        return res

    def save_users(self, users: Dict[str, object]):
        out = []
        for u in users.values():
            if hasattr(u, "to_dict"):
                out.append(u.to_dict())
            else:
                out.append(
                    {
                        "type": u.role(),
                        "username": u.username,
                        "password": getattr(u, "_password", ""),
                    }
                )
        self._write(out)

    def add_user(self, user):
        users = self.list_users()
        users[user.username] = user
        self.save_users(users)

    def remove_user(self, username: str):
        users = self.list_users()
        if username in users:
            users.pop(username)
            self.save_users(users)
            return True
        return False
