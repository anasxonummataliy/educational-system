import os
from signal import pause
import time
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

from utils import clear, header


def auth():
    clear()
    header("KIRISH")

    username = input(colored("Login: ", "cyan")).strip()
    user_rec = find_user(username)

    if not user_rec:
        print(colored("\n❌ Topilmadi", "red"))
        time.sleep(1)
        return None

    password = input(colored("Parol: ", "cyan"))
    user_obj = instantiate_user_from_record(user_rec)

    if user_obj and user_obj.authenticate(password):
        session.current_user = user_obj
        print(colored(f"\n✓ Xush kelibsiz: {user_obj.username}", "green"))
        time.sleep(1)
        return user_obj

    print(colored("\n❌ Xato parol", "red"))
    time.sleep(1)
    return None


def ensure_admin():
    data = load_data()
    if not data.get("users"):
        add_user(Admin("admin", "admin"))


def run_cli():
    ensure_admin()

    while True:
        clear()
        header("TA'LIM TIZIMI")
        print(colored("1. Kirish\n2. Chiqish", "cyan"))

        match input(colored("\n> ", "cyan")).strip():
            case "1":
                if user := auth():
                    dispatch(user)
            case "2":
                clear()
                print(colored("\n👋 Xayr!\n", "magenta"))
                break
            case _:
                print(colored("\n❌ Xato tanlov", "red"))
                time.sleep(1)


def dispatch(user):
    try:
        match user.role:
            case "Admin":
                admin_menu(user)
            case "Teacher":
                teacher_menu(user)
            case "Student":
                student_menu(user)
    except PermissionError as e:
        print(colored(f"\n❌ {e}", "red"))
        session.current_user = None
        time.sleep(2)


@decorators.require_role("Admin")
@decorators.log_action
def admin_menu(admin: Admin):
    actions = {
        "1": create_user,
        "2": remove_user,
        "3": reset_password,
        "4": view_logs,
    }

    while True:
        clear()
        header(f"ADMIN - {admin.username}")
        print(
            colored(
                "1. Yaratish\n2. O'chirish\n3. Parol\n4. Loglar\n5. Chiqish", "cyan"
            )
        )

        choice = input(colored("\n> ", "cyan")).strip()

        match choice:
            case "5":
                session.current_user = None
                break
            case _ if choice in actions:
                actions[choice]()
                pause()
            case _:
                print(colored("\n❌ Xato", "red"))
                time.sleep(1)


def create_user():
    clear()
    header("YANGI FOYDALANUVCHI")

    uname = input(colored("Login: ", "cyan")).strip()
    if find_user(uname):
        print(colored("\n❌ Mavjud", "red"))
        return

    print(colored("\n1. Admin\n2. Teacher\n3. Student", "cyan"))
    role_choice = input(colored("\n> ", "cyan")).strip()

    match role_choice:
        case "1":
            role, obj = "Admin", Admin
        case "2":
            role, obj = "Teacher", Teacher
        case "3":
            role, obj = "Student", Student
        case _:
            print(colored("\n❌ Xato tanlov", "red"))
            return

    pwd = input(colored("Parol: ", "cyan"))
    add_user(obj(uname, pwd))
    print(colored(f"\n✓ Yaratildi: {uname} ({role})", "green"))


def remove_user():
    clear()
    header("O'CHIRISH")

    uname = input(colored("Login: ", "cyan")).strip()

    if uname == session.current_user.username:
        print(colored("\n❌ O'zingizni o'chira olmaysiz", "red"))
        return

    confirm = (
        input(colored(f"\n'{uname}' o'chirilsinmi? (ha/yo'q): ", "yellow"))
        .strip()
        .lower()
    )

    match confirm:
        case "ha":
            if delete_user(uname):
                print(colored(f"\n✓ O'chirildi", "green"))
            else:
                print(colored(f"\n❌ Topilmadi", "red"))
        case _:
            print(colored("\n↩ Bekor qilindi", "yellow"))


def reset_password():
    clear()
    header("PAROL TIKLASH")

    uname = input(colored("Login: ", "cyan")).strip()

    if not find_user(uname):
        print(colored(f"\n❌ Topilmadi", "red"))
        return

    new_pwd = input(colored("Yangi parol: ", "cyan"))

    if update_user(uname, {"password": new_pwd}):
        print(colored(f"\n✓ Yangilandi", "green"))
    else:
        print(colored("\n❌ Xato", "red"))


def view_logs():
    """Loglarni ko'rish"""
    clear()
    header("LOGLAR")

    if os.path.exists("data.log"):
        with open("data.log", encoding="utf-8") as f:
            logs = f.read()
            print(colored(logs if logs.strip() else "Bo'sh", "white"))
    else:
        print(colored("Loglar yo'q", "yellow"))


# ============= TEACHER MENU =============


@decorators.require_role("Teacher")
@decorators.log_action
def teacher_menu(teacher: Teacher):
    actions = {
        "1": lambda: record_attendance(teacher),
        "2": lambda: record_grade(teacher),
        "3": lambda: analyze_class(teacher),
    }

    while True:
        clear()
        header(f"O'QITUVCHI - {teacher.username}")
        print(colored("1. Davomat\n2. Baho\n3. Tahlil\n4. Chiqish", "cyan"))

        choice = input(colored("\n> ", "cyan")).strip()

        match choice:
            case "4":
                session.current_user = None
                break
            case _ if choice in actions:
                actions[choice]()
                pause()
            case _:
                print(colored("\n❌ Xato", "red"))
                time.sleep(1)


def record_attendance(teacher: Teacher):
    clear()
    header("DAVOMAT")

    sname = input(colored("Talaba: ", "cyan")).strip()
    rec = find_user(sname)

    if not rec or rec.get("role") != "Student":
        print(colored("\n❌ Talaba topilmadi", "red"))
        return

    student = instantiate_user_from_record(rec)
    teacher.record_attendance(student)
    update_user(sname, {"attendance": student._attendance})

    print(colored(f"\n✓ Yozildi: {sname}", "green"))


def record_grade(teacher: Teacher):
    clear()
    header("BAHO")

    sname = input(colored("Talaba: ", "cyan")).strip()
    rec = find_user(sname)

    if not rec or rec.get("role") != "Student":
        print(colored("\n❌ Talaba topilmadi", "red"))
        return

    student = instantiate_user_from_record(rec)
    task = input(colored("Vazifa: ", "cyan")).strip()

    try:
        grade = float(input(colored("Baho (0-100): ", "cyan")).strip())
        if not 0 <= grade <= 100:
            raise ValueError
    except ValueError:
        print(colored("\n❌ Noto'g'ri baho", "red"))
        return

    teacher.record_grade(student, task, grade)
    update_user(sname, {"grades": student._grades})

    print(colored(f"\n✓ Yozildi: {task} = {grade}", "green"))


def analyze_class(teacher: Teacher):
    clear()
    header("TAHLIL")

    students = [
        instantiate_user_from_record(u) for u in list_users() if u["role"] == "Student"
    ]

    if not students:
        print(colored("❌ Talabalar yo'q", "red"))
        return

    result = teacher.analyze_class(students)

    print(colored(f"📊 Talabalar: {len(students)}", "cyan"))

    if mean := result.get("class_mean"):
        print(colored(f"📈 O'rtacha: {mean:.2f}", "cyan"))

    if median := result.get("class_median"):
        print(colored(f"📊 Median: {median:.2f}", "cyan"))

    if at_risk := result.get("at_risk"):
        print(colored(f"\n⚠ Xavf ({len(at_risk)}):", "yellow"))
        for s in at_risk:
            print(colored(f"  • {s}", "yellow"))
    else:
        print(colored("\n✓ Xavf yo'q", "green"))

    with open("class_report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["O'rtacha", result.get("class_mean")])
        writer.writerow(["Median", result.get("class_median")])
        writer.writerow(["Xavf", ";".join(at_risk)])

    print(colored("\n✓ Saqlandi: class_report.csv", "green"))



@decorators.require_role("Student")
@decorators.log_action
def student_menu(student: Student):
    actions = {
        "1": lambda: view_progress(student),
        "2": lambda: view_attendance(student),
        "3": lambda: export_report(student),
    }

    while True:
        clear()
        header(f"TALABA - {student.username}")
        print(colored("1. Taraqqiyot\n2. Davomat\n3. Eksport\n4. Chiqish", "cyan"))

        choice = input(colored("\n> ", "cyan")).strip()

        match choice:
            case "4":
                session.current_user = None
                break
            case _ if choice in actions:
                actions[choice]()
                pause()
            case _:
                print(colored("\n❌ Xato", "red"))
                time.sleep(1)


def view_progress(student: Student):
    clear()
    header("TARAQQIYOT")

    progress = student.view_progress()

    if avg := progress.get("average"):
        print(colored(f"📊 O'rtacha: {avg:.2f}", "cyan", attrs=["bold"]))
    else:
        print(colored("📊 O'rtacha: N/A", "yellow"))

    if grades := progress.get("grades"):
        print(colored("\n📚 Baholar:", "cyan"))
        for task, grade in grades.items():
            print(colored(f"  • {task}: {grade}", "white"))
    else:
        print(colored("\n❌ Baholar yo'q", "yellow"))


def view_attendance(student: Student):
    clear()
    header("DAVOMAT")

    attendance = student.view_attendance()

    if dates := attendance.get("attendance"):
        print(colored(f"✓ Kunlar: {len(dates)}", "cyan", attrs=["bold"]))
        print(colored("\n📅 Sanalar:", "cyan"))
        for date in dates:
            print(colored(f"  • {date}", "white"))
    else:
        print(colored("❌ Davomat yo'q", "yellow"))


def export_report(student: Student):
    clear()
    header("EKSPORT")

    filename = f"report_{student.username}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write("TALABA HISOBOTI\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Talaba: {student.username}\n")
        f.write(f"O'rtacha: {student.average or 'N/A'}\n\n")
        f.write("BAHOLAR:\n" + "-" * 30 + "\n")

        if student.grades:
            for task, grade in student.grades.items():
                f.write(f"{task}: {grade}\n")
        else:
            f.write("Yo'q\n")

        f.write("\n" + "=" * 50 + "\n")

    print(colored(f"✓ Saqlandi: {filename}", "green"))
