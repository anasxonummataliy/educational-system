import getpass
import os
from storage import (
    list_users,
    find_user,
    add_user,
    instantiate_user_from_record,
    update_user,
    delete_user,
    load_data,
)
from models import Student, Teacher, Admin
import decorators
import session
import csv
from termcolor import colored


def clear_console():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def authenticate() -> object:
    username = input(colored("Foydalanuvchi: ", "cyan")).strip()
    user_rec = find_user(username)
    if not user_rec:
        print(colored("Foydalanuvchi topilmadi", "red"))
        return None
    password = getpass.getpass(colored("Parol: ", "cyan"))
    user_obj = instantiate_user_from_record(user_rec)
    if user_obj and user_obj.authenticate(password):
        session.current_user = user_obj
        print(colored(f"Tizimga kirdi: {user_obj.username} ({user_obj.role})", "green"))
        return user_obj
    print(colored("Kirish muvaffaqiyatsiz", "red"))
    return None


def ensure_sample_admin():
    data = load_data()
    if not data.get("users"):
        admin = Admin("admin", "admin")
        add_user(admin)
        print(colored("Yaratildi: admin/admin", "yellow"))


def run_cli():
    ensure_sample_admin()
    while True:
        clear_console()
        print(colored("Konsol Ta'lim Tizimiga xush kelibsiz", "magenta"))
        print(colored("\n1) Kirish\n2) Chiqish", "cyan"))
        cmd = input(colored("Tanlang: ", "cyan")).strip()
        if cmd == "1":
            user = authenticate()
            if user:
                dispatch_menu(user)
        else:
            print(colored("Xayr", "magenta"))
            break


def dispatch_menu(user):
    try:
        if user.role == "Admin":
            admin_menu(user)
        elif user.role == "Teacher":
            teacher_menu(user)
        elif user.role == "Student":
            student_menu(user)
    except PermissionError as e:
        print(colored(f"Ruxsat xatosi: {e}", "red"))
        session.current_user = None


@decorators.require_role("Admin")
@decorators.log_action
def admin_menu(admin: Admin):
    while True:
        clear_console()
        print(
            colored(
                "\nAdmin menyu:\n1) Foydalanuvchi yaratish\n2) Foydalanuvchini o'chirish\n3) Parolni tiklash\n4) Yozuvlarni ko'rish\n5) Chiqish",
                "cyan",
            )
        )
        c = input(colored("Tanlang: ", "cyan")).strip()
        if c == "1":
            uname = input(colored("Yangi foydalanuvchi: ", "cyan")).strip()
            r = input(colored("Rol (Admin/Teacher/Student): ", "cyan")).strip()
            pwd = getpass.getpass(colored("Parol: ", "cyan"))
            if r == "Student":
                u = Student(uname, pwd)
            elif r == "Teacher":
                u = Teacher(uname, pwd)
            else:
                u = Admin(uname, pwd)
            add_user(u)
            print(colored("Foydalanuvchi yaratildi", "green"))
        elif c == "2":
            uname = input(colored("O'chirish uchun foydalanuvchi: ", "cyan")).strip()
            ok = delete_user(uname)
            print(colored("O`chirildi" if ok else "Topilmadi", "yellow"))
        elif c == "3":
            uname = input(
                colored("Parolni tiklash uchun foydalanuvchi: ", "cyan")
            ).strip()
            new = getpass.getpass(colored("Yangi parol: ", "cyan"))
            ok = update_user(uname, {"password": new})
            print(colored("Parol yangilandi" if ok else "Topilmadi", "yellow"))
        elif c == "4":
            if os.path.exists("data.log"):
                with open("data.log") as f:
                    print(colored("\n--- Yozuvlar ---", "magenta"))
                    print(f.read())
            else:
                print(colored("Hozircha yozuvlar yo'q", "yellow"))
        else:
            session.current_user = None
            break


@decorators.require_role("Teacher")
@decorators.log_action
def teacher_menu(teacher: Teacher):
    while True:
        clear_console()
        print(
            colored(
                "\nO'qituvchi menyu:\n1) Davomat yozish\n2) Bahoni yozish\n3) Sinf tahlili\n4) Chiqish",
                "cyan",
            )
        )
        c = input(colored("Tanlang: ", "cyan")).strip()
        if c == "1":
            sname = input(colored("Talaba foydalanuvchi: ", "cyan")).strip()
            rec = find_user(sname)
            if not rec:
                print(colored("Talaba topilmadi", "red"))
                continue
            student = instantiate_user_from_record(rec)
            teacher.record_attendance(student)
            update_user(sname, {"attendance": student._attendance})
            print(colored("Davomat yozildi", "green"))
        elif c == "2":
            sname = input(colored("Talaba foydalanuvchi: ", "cyan")).strip()
            rec = find_user(sname)
            if not rec:
                print(colored("Talaba topilmadi", "red"))
                continue
            student = instantiate_user_from_record(rec)
            asg = input(colored("Vazifa nomi: ", "cyan")).strip()
            try:
                g = float(input(colored("Baho: ", "cyan")).strip())
            except ValueError:
                print(colored("Noto`g`ri baho", "red"))
                continue
            teacher.record_grade(student, asg, g)
            update_user(sname, {"grades": student._grades})
            print(colored("Baho yozildi", "green"))
        elif c == "3":
            users = [
                instantiate_user_from_record(u)
                for u in list_users()
                if u["role"] == "Student"
            ]
            res = teacher.analyze_class(users)
            print(colored("Sinf tahlili:", "magenta"))
            print(colored(f"O'rtacha: {res.get('class_mean')}", "cyan"))
            print(colored(f"Median: {res.get('class_median')}", "cyan"))
            print(colored("Xavf ostidagi talabalar:", "yellow"))
            for s in res.get("at_risk", []):
                print(colored(f" - {s}", "yellow"))
            with open("reports_class.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["metric", "value"])
                writer.writerow(["O'rtacha", res.get("class_mean")])
                writer.writerow(["Median", res.get("class_median")])
                writer.writerow(["Xavf ostidagi", ";".join(res.get("at_risk", []))])
            print(colored("reports_class.csv saqlandi", "green"))
        else:
            session.current_user = None
            break


@decorators.require_role("Student")
@decorators.log_action
def student_menu(student: Student):
    while True:
        clear_console()
        print(
            colored(
                "\nTalaba menyu:\n1) Taraqqiyotni ko'rish\n2) Davomatni ko'rish\n3) Hisobot eksport qilish\n4) Chiqish",
                "cyan",
            )
        )
        c = input(colored("Tanlang: ", "cyan")).strip()
        if c == "1":
            p = student.view_progress()
            print(colored(f"O'rtacha: {p.get('average')}", "cyan"))
            print(colored("Baholar:", "cyan"))
            for k, v in p.get("grades", {}).items():
                print(colored(f" - {k}: {v}", "cyan"))
        elif c == "2":
            at = student.view_attendance()
            print(colored("Davomat:", "cyan"))
            for d in at.get("attendance", []):
                print(colored(f" - {d}", "cyan"))
        elif c == "3":
            fname = f"report_{student.username}.txt"
            with open(fname, "w") as f:
                f.write(
                    f"Talaba: {student.username}\nO'rtacha: {student.average}\nBaholar:\n"
                )
                for k, v in student.grades.items():
                    f.write(f"{k}: {v}\n")
            print(colored("Eksport qilindi: " + fname, "green"))
        else:
            session.current_user = None
            break
