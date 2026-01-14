from termcolor import colored
from models import Admin, Teacher, Student
from decorators import require_role, log_action
from dataclasses import dataclass
from reports import generate_student_report, generate_all_reports


@dataclass
class Session:
    storage: object
    current_user: object | None = None


class ConsoleUI:
    def __init__(self, storage):
        self.storage = storage
        self.session = Session(storage)

    def run(self):
        while True:
            try:
                self.show_welcome()
                if not self.login():
                    break
                self.route()
            except KeyboardInterrupt:
                print(colored("\nXayr.", "cyan"))
                break
            except Exception as e:
                print(colored(f"Xato: {e}", "red"))

    def show_welcome(self):
        print(colored("=== Universitet Talabalar Boshqaruvi Tizimi ===", "green"))

    def login(self) -> bool:
        users = self.storage.list_users()
        print(colored("Kirish (chiqish uchun 'exit' yozing):", "yellow"))
        uname = input("foydalanuvchi: ").strip()
        if uname.lower() in ("exit", "quit"):
            return False
        pwd = input("parol: ").strip()
        u = users.get(uname)
        if not u or not u.check_password(pwd):
            print(colored("Noto'g'ri ma'lumotlar", "red"))
            return True
        self.session.current_user = u
        print(colored(f"Xush kelibsiz {u.username} ({u.role()})", "cyan"))
        return True

    def route(self):
        role = self.session.current_user.role()
        if role == "admin":
            self.admin_menu()
        elif role == "teacher":
            self.teacher_menu()
        elif role == "student":
            self.student_menu()

    @log_action()
    @require_role("admin")
    def admin_menu(self):
        while True:
            print(
                colored(
                    "\nAdmin menyu: 1) Foydalanuvchi qo'shish 2) Foydalanuvchini o'chirish 3) Foydalanuvchilar ro'yxati 4) Chiqish",
                    "yellow",
                )
            )
            cmd = input("> ").strip()
            if cmd == "1":
                self._add_user()
            elif cmd == "2":
                self._remove_user()
            elif cmd == "3":
                self._list_users()
            elif cmd == "4":
                self.session.current_user = None
                break

    def _add_user(self):
        uname = input("yangi foydalanuvchi: ").strip()
        pwd = input("parol: ").strip()
        typ = input("tur (admin/teacher/student): ").strip()
        if typ == "admin":
            u = Admin(uname, pwd)
        elif typ == "teacher":
            u = Teacher(uname, pwd)
        else:
            u = Student(uname, pwd)
        self.storage.add_user(u)
        print(colored("Foydalanuvchi qo'shildi", "green"))

    def _remove_user(self):
        uname = input("o'chiriladigan foydalanuvchi: ").strip()
        ok = self.storage.remove_user(uname)
        print(colored("O'chirildi" if ok else "Topilmadi", "green" if ok else "red"))

    def _list_users(self):
        users = self.storage.list_users()
        for u in users.values():
            print(f"- {u.username} ({u.role()})")

    @log_action()
    @require_role("teacher")
    def teacher_menu(self):
        while True:
            print(
                colored(
                    "\nO'qituvchi menyusi: 1) Davomat belgilash 2) Baho qo'shish 3) Talaba hisobot 4) Chiqish",
                    "yellow",
                )
            )
            cmd = input("> ").strip()
            if cmd == "1":
                self._mark_attendance()
            elif cmd == "2":
                self._add_grade()
            elif cmd == "3":
                self._student_report()
            elif cmd == "4":
                self.session.current_user = None
                break

    def _find_student(self, username: str):
        users = self.storage.list_users()
        u = users.get(username)
        if not u or not isinstance(u, Student):
            print(colored("Talaba topilmadi", "red"))
            return None
        return u

    def _mark_attendance(self):
        uname = input("talaba foydalanuvchi: ").strip()
        s = self._find_student(uname)
        if not s:
            return
        val = input("davomat bormi? (y/n): ").strip().lower() in ("y", "yes")
        s.add_attendance(val)
        users = self.storage.list_users()
        users[s.username] = s
        self.storage.save_users(users)
        print(colored("Davomat saqlandi", "green"))

    def _add_grade(self):
        uname = input("talaba foydalanuvchi: ").strip()
        s = self._find_student(uname)
        if not s:
            return
        try:
            g = float(input("baho (0-100): ").strip())
        except ValueError:
            print(colored("Noto'g'ri baho", "red"))
            return
        s.add_grade(g)
        users = self.storage.list_users()
        users[s.username] = s
        self.storage.save_users(users)
        print(colored("Baho qo'shildi", "green"))

    @log_action()
    def _student_report(self):
        uname = input("talaba foydalanuvchi: ").strip()
        s = self._find_student(uname)
        if not s:
            return
        print(colored(f"{s.username} uchun hisobot", "cyan"))
        print("O'rtacha:", colored(f"{s.average:.2f}", "magenta"))
        print("Davomat yozuvlari:", len(s.attendance))
        if s.at_risk():
            print(colored("Akademik xavf: HA", "red"))
        else:
            print(colored("Akademik xavf: YO'Q", "green"))
        try:
            txt_path, csv_path = generate_student_report(s)
            print(colored(f"Hisobot saqlandi: {txt_path} va {csv_path}", "green"))
        except Exception as e:
            print(colored(f"Hisobotni saqlash muvaffaqiyatsiz: {e}", "red"))

    @log_action()
    @require_role("student")
    def student_menu(self):
        s = self.session.current_user
        while True:
            print(
                colored(
                    "\nTalaba menyusi: 1) Taraqqiyotni ko'rish 2) Chiqish", "yellow"
                )
            )
            cmd = input("> ").strip()
            if cmd == "1":
                self._view_progress(s)
            elif cmd == "2":
                self.session.current_user = None
                break

    def _view_progress(self, s: Student):
        print(colored(f"Talaba: {s.username}", "cyan"))
        print("O'rtacha:", colored(f"{s.average:.2f}", "magenta"))
        print("Baholar:", ", ".join(str(g) for g in s.grades) or "yo'q")
        print("Davomat yozuvlari:", len(s.attendance))
        if s.at_risk():
            print(
                colored(
                    "Siz akademik xavf ostidasiz. Maslahatchi bilan bog'laning.", "red"
                )
            )
        try:
            txt_path, csv_path = generate_student_report(s)
            print(
                colored(
                    f"Sizning hisobotingiz saqlandi: {txt_path} va {csv_path}", "green"
                )
            )
        except Exception as e:
            print(
                colored(f"Sizning hisobotingizni saqlash muvaffaqiyatsiz: {e}", "red")
            )
