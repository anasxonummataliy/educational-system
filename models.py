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


class Subject:
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code
        self.teacher = None
        self.students: List[str] = []

    def to_dict(self):
        return {
            "name": self.name,
            "code": self.code,
            "teacher": self.teacher,
            "students": self.students,
        }

    @staticmethod
    def from_dict(data):
        subject = Subject(data["name"], data["code"])
        subject.teacher = data.get("teacher")
        subject.students = data.get("students", [])
        return subject


class Student(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Student")
        self._grades: Dict[str, Dict[str, float]] = {}
        self._attendance: Dict[str, List[str]] = {}

    @property
    def grades(self) -> Dict[str, Dict[str, float]]:
        return dict(self._grades)

    @property
    def attendance(self) -> Dict[str, List[str]]:
        return dict(self._attendance)

    def add_attendance(self, subject_code: str, date_str: str = None):
        date_str = date_str or datetime.date.today().isoformat()
        if subject_code not in self._attendance:
            self._attendance[subject_code] = []
        self._attendance[subject_code].append(date_str)

    def add_grade(self, subject_code: str, assignment: str, grade: float):
        if subject_code not in self._grades:
            self._grades[subject_code] = {}
        self._grades[subject_code][assignment] = float(grade)

    def average_by_subject(self, subject_code: str):
        if subject_code not in self._grades or not self._grades[subject_code]:
            return None
        return statistics.mean(self._grades[subject_code].values())

    @property
    def overall_average(self):
        all_grades = []
        for subject_grades in self._grades.values():
            all_grades.extend(subject_grades.values())
        if not all_grades:
            return None
        return statistics.mean(all_grades)

    def menu_options(self):
        return {
            "view_progress": self.view_progress,
            "view_attendance": self.view_attendance,
        }

    def view_progress(self):
        return {"overall_average": self.overall_average, "grades": self.grades}

    def view_attendance(self):
        return {"attendance": self.attendance}


class Teacher(User):
    def __init__(self, username: str, password: str, subjects: List[str] = None):
        super().__init__(username, password, role="Teacher")
        self.subjects = subjects or []

    def record_attendance(
        self, student: Student, subject_code: str, date_str: str = None
    ):
        student.add_attendance(subject_code, date_str)

    def record_grade(
        self, student: Student, subject_code: str, assignment: str, grade: float
    ):
        student.add_grade(subject_code, assignment, grade)

    def analyze_subject(self, students: List[Student], subject_code: str):
        averages = [
            s.average_by_subject(subject_code)
            for s in students
            if s.average_by_subject(subject_code) is not None
        ]
        return {
            "subject_mean": statistics.mean(averages) if averages else None,
            "subject_median": statistics.median(averages) if averages else None,
            "students_count": len(students),
        }

    def menu_options(self):
        return {
            "record_attendance": self.record_attendance,
            "record_grade": self.record_grade,
            "analyze_subject": self.analyze_subject,
        }


class Admin(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password, role="Admin")

    def menu_options(self):
        return {
            "create_user": None,
            "create_subject": None,
            "assign_teacher": None,
            "enroll_student": None,
        }
