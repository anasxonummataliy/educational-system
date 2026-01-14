from abc import ABC, abstractmethod


class User(ABC):
    def __init__(self, user_id, name, role, password):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.__password = password  # Inkapsulyatsiya

    @abstractmethod
    def display_menu(self):
        pass

    def check_password(self, password):
        return self.__password == password

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "role": self.role,
            "password": self.__password,
        }


class Student(User):
    def __init__(self, user_id, name, password, grades=None, attendance=None):
        super().__init__(user_id, name, "Student", password)
        self.grades = grades if grades else {}
        self.attendance = attendance if attendance else []

    def display_menu(self):
        print(f"\n--- Student Menu ({self.name}) ---")
        print("1. View Grades\n2. View Attendance\n3. Logout")

    def to_dict(self):
        data = super().to_dict()
        data.update({"grades": self.grades, "attendance": self.attendance})
        return data


class Teacher(User):
    def __init__(self, user_id, name, password):
        super().__init__(user_id, name, "Teacher", password)

    def display_menu(self):
        print(f"\n--- Teacher Menu ({self.name}) ---")
        print("1. Mark Attendance\n2. Assign Grade\n3. View Analytics\n4. Logout")


class Admin(User):
    def __init__(self, user_id, name, password):
        super().__init__(user_id, name, "Admin", password)

    def display_menu(self):
        print(f"\n--- Admin Menu ({self.name}) ---")
        print("1. Add User\n2. Delete User\n3. View Logs\n4. Logout")
