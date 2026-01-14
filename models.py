from abc import ABC, abstractmethod
from typing import List
from datetime import date


class User(ABC):
    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password

    @property
    def username(self):
        return self._username

    def check_password(self, pwd: str) -> bool:
        return self._password == pwd

    @abstractmethod
    def role(self) -> str:
        raise NotImplementedError()


class Admin(User):
    def role(self) -> str:
        return "admin"


class Teacher(User):
    def role(self) -> str:
        return "teacher"


class Student(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        self._grades: List[float] = []
        self._attendance: List[str] = [] 

    def role(self) -> str:
        return "student"

    def add_grade(self, value: float):
        self._grades.append(float(value))

    def add_attendance(self, present: bool, for_date: str | None = None):
        d = for_date or date.today().isoformat()
        self._attendance.append(f"{d}:{int(bool(present))}")

    @property
    def grades(self) -> List[float]:
        return list(self._grades)

    @property
    def attendance(self) -> List[str]:
        return list(self._attendance)

    @property
    def average(self) -> float:
        if not self._grades:
            return 0.0
        return sum(self._grades) / len(self._grades)

    def at_risk(self, threshold: float = 50.0) -> bool:
        return self.average < threshold

    def to_dict(self):
        return {
            "type": "student",
            "username": self._username,
            "password": self._password,
            "grades": self._grades,
            "attendance": self._attendance,
        }

    @staticmethod
    def from_dict(d: dict):
        s = Student(d["username"], d.get("password", ""))
        s._grades = d.get("grades", [])
        s._attendance = d.get("attendance", [])
        return s
