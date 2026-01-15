from abc import ABC, abstractmethod
from typing import Dict, List
import statistics
import datetime


class User(ABC):
    def __init__(self, username: str, password: str, role: str):
        self.username = username
        self._password = password
        self.role = role.strip().capitalize()

    def authenticate(self, password: str) -> bool:
        return self._password == password

    def set_password(self, new_password: str):
        self._password = new_password

    @abstractmethod
    def menu_options(self) -> Dict:
        pass


class Student(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Student")
        self._grades: Dict[str, float] = {}
        self._attendance: List[str] = []

    @property
    def grades(self) -> Dict[str, float]:
        return dict(self._grades)

    @property
    def attendance(self) -> List[str]:
        return list(self._attendance)

    def add_attendance(self, date_str: str = None):
        date_str = date_str or datetime.date.today().isoformat()
        self._attendance.append(date_str)

    def add_grade(self, assignment: str, grade: float):
        self._grades[assignment] = float(grade)

    @property
    def average(self):
        if not self._grades:
            return None
        return statistics.mean(self._grades.values())

    def at_academic_risk(
        self,
        grade_threshold: float = 50.0,
        min_attendance: float = 0.7,
        expected_sessions: int = 10,
    ):
        avg = self.average
        if avg is None:
            return True
        attendance_rate = len(self._attendance) / expected_sessions
        return avg < grade_threshold or attendance_rate < min_attendance

    def menu_options(self):
        return {
            "view_progress": self.view_progress,
            "view_attendance": self.view_attendance,
        }

    def view_progress(self):
        return {"average": self.average, "grades": self.grades}

    def view_attendance(self):
        return {"attendance": self.attendance}


class Teacher(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Teacher")

    def record_attendance(self, student: Student, date_str: str = None):
        student.add_attendance(date_str)

    def record_grade(self, student: Student, assignment: str, grade: float):
        student.add_grade(assignment, grade)

    def analyze_class(self, students: List[Student]):
        averages = [s.average for s in students if s.average is not None]
        return {
            "class_mean": statistics.mean(averages) if averages else None,
            "class_median": statistics.median(averages) if averages else None,
            "at_risk": [s.username for s in students if s.at_academic_risk()],
        }

    def menu_options(self):
        return {
            "record_attendance": self.record_attendance,
            "record_grade": self.record_grade,
            "analyze_class": self.analyze_class,
        }


class Admin(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Admin")

    def menu_options(self):
        return {
            "create_user": None,
            "delete_user": None,
            "reset_password": None,
            "view_logs": None,
        }
