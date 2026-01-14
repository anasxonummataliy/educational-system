from models import Admin
from storage import load_data, save_data
import ui


class UniversitySystem:
    def __init__(self):
        self.users = load_data()
        self.current_user = None

    def login(self):
        print("\n--- Universitet Tizimiga Kirish ---")
        uid = input("User ID: ")
        pwd = input("Password: ")
        for user in self.users:
            if user.user_id == uid and user.check_password(pwd):
                self.current_user = user
                return True
        print("Xato: Login yoki parol noto'g'ri!")
        return False

    def start(self):
        # Agar tizimda hech kim bo'lmasa, admin yaratish
        if not self.users:
            admin = Admin("admin", "Asosiy Admin", "1234")
            self.users.append(admin)
            save_data(self.users)

        while True:
            if not self.current_user:
                if not self.login():
                    continue

            # Rolga qarab UI menyularini chaqirish (Polimorfizm elementi)
            if self.current_user.role == "Admin":
                ui.admin_menu(self, self.current_user)
            elif self.current_user.role == "Teacher":
                ui.teacher_menu(self, self.current_user)
            elif self.current_user.role == "Student":
                ui.student_menu(self.current_user)

            self.current_user = None  # Logoutdan keyin login menyusiga qaytish


if __name__ == "__main__":
    app = UniversitySystem()
    app.start()
