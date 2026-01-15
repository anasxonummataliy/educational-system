import os
import csv
import statistics
import time
import session
import decorators

from utils import pause, clear, header
from termcolor import colored
from models import Student, Subject, Teacher, Admin
from storage import (
    add_subject,
    find_subject,
    list_subjects,
    list_users,
    find_user,
    add_user,
    instantiate_user_from_record,
    update_subject,
    update_user,
    delete_user,
    load_data,
)


def authenticate():
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
                if user := authenticate():
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
        "2": create_subject,
        "3": assign_teacher,
        "4": enroll_student,
        "5": view_all_subjects,
        "6": remove_user,
        "7": reset_password,
        "8": view_logs,
    }

    while True:
        clear()
        header(f"ADMIN - {admin.username}")
        print(colored("1. User yaratish", "cyan"))
        print(colored("2. Fan yaratish", "cyan"))
        print(colored("3. O'qituvchi tayinlash", "cyan"))
        print(colored("4. Talaba yozish", "cyan"))
        print(colored("5. Fanlar", "cyan"))
        print(colored("6. User o'chirish", "cyan"))
        print(colored("7. Parol", "cyan"))
        print(colored("8. Loglar", "cyan"))
        print(colored("9. Chiqish", "cyan"))

        choice = input(colored("\n> ", "cyan")).strip()

        match choice:
            case "9":
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
    header("YANGI USER")

    uname = input(colored("Login: ", "cyan")).strip()
    if find_user(uname):
        print(colored("\n❌ Mavjud", "red"))
        return

    print(colored("\n1. Admin\n2. Teacher\n3. Student", "cyan"))
    role_choice = input(colored("\n> ", "cyan")).strip()

    pwd = input(colored("Parol: ", "cyan"))

    match role_choice:
        case "1":
            obj = Admin(uname, pwd)
            role = "Admin"
        case "2":
            obj = Teacher(uname, pwd)
            role = "Teacher"
        case "3":
            obj = Student(uname, pwd)
            role = "Student"
        case _:
            print(colored("\n❌ Xato tanlov", "red"))
            return

    add_user(obj)
    print(colored(f"\n✓ Yaratildi: {uname} ({role})", "green"))


def create_subject():
    clear()
    header("YANGI FAN")

    code = input(colored("Fan kodi (MATH101): ", "cyan")).strip().upper()
    if find_subject(code):
        print(colored("\n❌ Bu kod mavjud", "red"))
        return

    name = input(colored("Fan nomi: ", "cyan")).strip()

    subject = Subject(name, code)
    add_subject(subject)
    print(colored(f"\n✓ Yaratildi: {name} ({code})", "green"))


def assign_teacher():
    clear()
    header("O'QITUVCHI TAYINLASH")

    subjects = list_subjects()
    if not subjects:
        print(colored("❌ Fanlar yo'q", "red"))
        return

    print(colored("Fanlar:", "cyan"))
    for s in subjects:
        teacher = s.get("teacher", "Yo'q")
        print(colored(f"  [{s['code']}] {s['name']} - {teacher}", "white"))

    code = input(colored("\nFan kodi: ", "cyan")).strip().upper()
    subject = find_subject(code)

    if not subject:
        print(colored("\n❌ Fan topilmadi", "red"))
        return

    teachers = [u for u in list_users() if u.get("role") == "Teacher"]
    if not teachers:
        print(colored("\n❌ O'qituvchilar yo'q", "red"))
        return

    print(colored("\nO'qituvchilar:", "cyan"))
    for t in teachers:
        subjects_list = ", ".join(t.get("subjects", [])) or "Yo'q"
        print(colored(f"  - {t['username']} ({subjects_list})", "white"))

    teacher_name = input(colored("\nO'qituvchi: ", "cyan")).strip()
    teacher_rec = find_user(teacher_name)

    if not teacher_rec or teacher_rec.get("role") != "Teacher":
        print(colored("\n❌ Topilmadi", "red"))
        return

    update_subject(code, {"teacher": teacher_name})

    teacher_subjects = teacher_rec.get("subjects", [])
    if code not in teacher_subjects:
        teacher_subjects.append(code)
        update_user(teacher_name, {"subjects": teacher_subjects})

    print(colored(f"\n✓ {teacher_name} -> {subject['name']}", "green"))


def enroll_student():
    clear()
    header("TALABA YOZISH")

    subjects = list_subjects()
    if not subjects:
        print(colored("❌ Fanlar yo'q", "red"))
        return

    print(colored("Fanlar:", "cyan"))
    for s in subjects:
        count = len(s.get("students", []))
        print(colored(f"  [{s['code']}] {s['name']} ({count} talaba)", "white"))

    code = input(colored("\nFan kodi: ", "cyan")).strip().upper()
    subject = find_subject(code)

    if not subject:
        print(colored("\n❌ Fan topilmadi", "red"))
        return

    students = [u for u in list_users() if u.get("role") == "Student"]
    if not students:
        print(colored("\n❌ Talabalar yo'q", "red"))
        return

    print(colored("\nTalabalar:", "cyan"))
    for st in students:
        print(colored(f"  - {st['username']}", "white"))

    student_name = input(colored("\nTalaba: ", "cyan")).strip()
    student_rec = find_user(student_name)

    if not student_rec or student_rec.get("role") != "Student":
        print(colored("\n❌ Topilmadi", "red"))
        return

    enrolled = subject.get("students", [])
    if student_name in enrolled:
        print(colored("\n❌ Allaqachon yozilgan", "yellow"))
        return

    enrolled.append(student_name)
    update_subject(code, {"students": enrolled})

    print(colored(f"\n✓ {student_name} -> {subject['name']}", "green"))


def view_all_subjects():
    clear()
    header("FANLAR")

    subjects = list_subjects()
    if not subjects:
        print(colored("❌ Fanlar yo'q", "red"))
        return

    for s in subjects:
        print(colored(f"\n📚 {s['name']} [{s['code']}]", "cyan", attrs=["bold"]))
        print(colored(f"   O'qituvchi: {s.get('teacher', 'Yo\'q')}", "white"))
        students = s.get("students", [])
        print(
            colored(
                f"   Talabalar ({len(students)}): {', '.join(students) if students else 'Yo\'q'}",
                "white",
            )
        )


def remove_user():
    clear()
    header("USER O'CHIRISH")

    uname = input(colored("Login: ", "cyan")).strip()

    if uname == session.current_user.username:
        print(colored("\n❌ O'zingizni o'chira olmaysiz", "red"))
        return

    confirm = (
        input(colored(f"\n'{uname}' o'chirilsinmi? (ha/yo'q): ", "yellow"))
        .strip()
        .lower()
    )

    if confirm == "ha":
        if delete_user(uname):
            print(colored("\n✓ O'chirildi", "green"))
        else:
            print(colored("\n❌ Topilmadi", "red"))
    else:
        print(colored("\n↩ Bekor qilindi", "yellow"))


def reset_password():
    clear()
    header("PAROL")

    uname = input(colored("Login: ", "cyan")).strip()

    if not find_user(uname):
        print(colored("\n❌ Topilmadi", "red"))
        return

    new_pwd = input(colored("Yangi parol: ", "cyan"))

    if update_user(uname, {"password": new_pwd}):
        print(colored("\n✓ Yangilandi", "green"))
    else:
        print(colored("\n❌ Xato", "red"))


def view_logs():
    clear()
    header("LOGLAR")

    if os.path.exists("data.log"):
        with open("data.log", encoding="utf-8") as f:
            logs = f.read()
            print(colored(logs if logs.strip() else "Bo'sh", "white"))
    else:
        print(colored("Loglar yo'q", "yellow"))


@decorators.require_role("Teacher")
@decorators.log_action
def teacher_menu(teacher: Teacher):
    actions = {
        "1": lambda: my_subjects(teacher),
        "2": lambda: add_attendance(teacher),
        "3": lambda: add_grade(teacher),
        "4": lambda: subject_analysis(teacher),
    }

    while True:
        clear()
        header(f"O'QITUVCHI - {teacher.username}")
        print(colored("1. Mening fanlarim", "cyan"))
        print(colored("2. Davomat", "cyan"))
        print(colored("3. Baho", "cyan"))
        print(colored("4. Tahlil", "cyan"))
        print(colored("5. Chiqish", "cyan"))

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


def my_subjects(teacher: Teacher):
    clear()
    header("MENING FANLARIM")

    if not teacher.subjects:
        print(colored("❌ Sizga fan tayinlanmagan", "yellow"))
        return

    for code in teacher.subjects:
        subject = find_subject(code)
        if subject:
            students = subject.get("students", [])
            print(colored(f"\n📚 {subject['name']} [{code}]", "cyan", attrs=["bold"]))
            print(colored(f"   Talabalar ({len(students)}):", "white"))
            if students:
                for s in students:
                    print(colored(f"     • {s}", "white"))
            else:
                print(colored("     Yo'q", "yellow"))


def add_attendance(teacher: Teacher):
    clear()
    header("DAVOMAT")

    if not teacher.subjects:
        print(colored("❌ Sizga fan tayinlanmagan", "yellow"))
        return

    print(colored("Fanlaringiz:", "cyan"))
    for code in teacher.subjects:
        subject = find_subject(code)
        if subject:
            print(colored(f"  [{code}] {subject['name']}", "white"))

    code = input(colored("\nFan: ", "cyan")).strip().upper()

    if code not in teacher.subjects:
        print(colored("\n❌ Bu fan sizga tegishli emas", "red"))
        return

    subject = find_subject(code)
    if not subject:
        print(colored("\n❌ Fan topilmadi", "red"))
        return

    students = subject.get("students", [])
    if not students:
        print(colored("\n❌ Talabalar yo'q", "red"))
        return

    print(colored("\nTalabalar:", "cyan"))
    for s in students:
        print(colored(f"  - {s}", "white"))

    sname = input(colored("\nTalaba: ", "cyan")).strip()

    if sname not in students:
        print(colored("\n❌ Bu talaba bu fanda emas", "red"))
        return

    rec = find_user(sname)
    student = instantiate_user_from_record(rec)
    teacher.record_attendance(student, code)
    update_user(sname, {"attendance": student._attendance})

    print(colored(f"\n✓ Davomat yozildi", "green"))


def add_grade(teacher: Teacher):
    clear()
    header("BAHO")

    if not teacher.subjects:
        print(colored("❌ Sizga fan tayinlanmagan", "yellow"))
        return

    print(colored("Fanlaringiz:", "cyan"))
    for code in teacher.subjects:
        subject = find_subject(code)
        if subject:
            print(colored(f"  [{code}] {subject['name']}", "white"))

    code = input(colored("\nFan: ", "cyan")).strip().upper()

    if code not in teacher.subjects:
        print(colored("\n❌ Bu fan sizga tegishli emas", "red"))
        return

    subject = find_subject(code)
    if not subject:
        print(colored("\n❌ Fan topilmadi", "red"))
        return

    students = subject.get("students", [])
    if not students:
        print(colored("\n❌ Talabalar yo'q", "red"))
        return

    print(colored("\nTalabalar:", "cyan"))
    for s in students:
        print(colored(f"  - {s}", "white"))

    sname = input(colored("\nTalaba: ", "cyan")).strip()

    if sname not in students:
        print(colored("\n❌ Bu talaba bu fanda emas", "red"))
        return

    rec = find_user(sname)
    student = instantiate_user_from_record(rec)

    task = input(colored("Vazifa: ", "cyan")).strip()

    try:
        grade = float(input(colored("Baho (0-100): ", "cyan")).strip())
        if not 0 <= grade <= 100:
            raise ValueError
    except ValueError:
        print(colored("\n❌ Noto'g'ri baho", "red"))
        return

    teacher.record_grade(student, code, task, grade)
    update_user(sname, {"grades": student._grades})

    print(colored(f"\n✓ Baho yozildi: {task} = {grade}", "green"))


def subject_analysis(teacher: Teacher):
    clear()
    header("TAHLIL")

    if not teacher.subjects:
        print(colored("❌ Sizga fan tayinlanmagan", "yellow"))
        return

    print(colored("Fanlaringiz:", "cyan"))
    for code in teacher.subjects:
        subject = find_subject(code)
        if subject:
            print(colored(f"  [{code}] {subject['name']}", "white"))

    code = input(colored("\nFan: ", "cyan")).strip().upper()

    if code not in teacher.subjects:
        print(colored("\n❌ Bu fan sizga tegishli emas", "red"))
        return

    subject = find_subject(code)
    if not subject:
        print(colored("\n❌ Fan topilmadi", "red"))
        return

    student_names = subject.get("students", [])
    if not student_names:
        print(colored("\n❌ Talabalar yo'q", "red"))
        return

    students = [
        instantiate_user_from_record(find_user(name))
        for name in student_names
        if find_user(name)
    ]

    result = teacher.analyze_subject(students, code)

    print(colored(f"\n📚 {subject['name']} [{code}]", "cyan", attrs=["bold"]))
    print(colored(f"📊 Talabalar: {result.get('students_count')}", "cyan"))

    if mean := result.get("subject_mean"):
        print(colored(f"📈 O'rtacha: {mean:.2f}", "cyan"))
    else:
        print(colored("📈 O'rtacha: N/A", "yellow"))

    if median := result.get("subject_median"):
        print(colored(f"📊 Median: {median:.2f}", "cyan"))
    else:
        print(colored("📊 Median: N/A", "yellow"))

    with open(f"report_{code}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Fan", subject["name"]])
        writer.writerow(["Kod", code])
        writer.writerow(["Talabalar", result.get("students_count")])
        writer.writerow(["O'rtacha", result.get("subject_mean")])
        writer.writerow(["Median", result.get("subject_median")])

    print(colored(f"\n✓ Saqlandi: report_{code}.csv", "green"))


@decorators.require_role("Student")
@decorators.log_action
def student_menu(student: Student):
    actions = {
        "1": lambda: show_progress(student),
        "2": lambda: show_attendance(student),
        "3": lambda: export_report(student),
    }

    while True:
        clear()
        header(f"TALABA - {student.username}")
        print(colored("1. Baholar", "cyan"))
        print(colored("2. Davomat", "cyan"))
        print(colored("3. Eksport", "cyan"))
        print(colored("4. Chiqish", "cyan"))

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


def show_progress(student: Student):
    clear()
    header("BAHOLAR")

    progress = student.view_progress()

    if avg := progress.get("overall_average"):
        print(colored(f"📊 Umumiy o'rtacha: {avg:.2f}\n", "cyan", attrs=["bold"]))
    else:
        print(colored("📊 Umumiy o'rtacha: N/A\n", "yellow"))

    grades = progress.get("grades", {})

    if not grades:
        print(colored("❌ Baholar yo'q", "yellow"))
        return

    for subject_code, subject_grades in grades.items():
        subject = find_subject(subject_code)
        subject_name = subject["name"] if subject else subject_code

        print(colored(f"📚 {subject_name} [{subject_code}]", "cyan"))

        if subject_grades:
            subject_avg = statistics.mean(subject_grades.values())
            print(colored(f"   O'rtacha: {subject_avg:.2f}", "white"))
            for task, grade in subject_grades.items():
                print(colored(f"   • {task}: {grade}", "white"))
        else:
            print(colored("   Baholar yo'q", "yellow"))
        print()


def show_attendance(student: Student):
    clear()
    header("DAVOMAT")

    attendance = student.view_attendance()
    att_data = attendance.get("attendance", {})

    if not att_data:
        print(colored("❌ Davomat yo'q", "yellow"))
        return

    for subject_code, dates in att_data.items():
        subject = find_subject(subject_code)
        subject_name = subject["name"] if subject else subject_code

        print(colored(f"\n📚 {subject_name} [{subject_code}]", "cyan"))
        print(colored(f"   Kunlar: {len(dates)}", "white"))
        for date in dates:
            print(colored(f"   • {date}", "white"))


def export_report(student: Student):
    clear()
    header("EKSPORT")

    filename = f"report_{student.username}.txt"

    with open(filename, "w") as f:
        f.write("=" * 50 + "\n")
        f.write("TALABA HISOBOTI\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Talaba: {student.username}\n")
        f.write(f"Umumiy o'rtacha: {student.overall_average or 'N/A'}\n\n")

        f.write("BAHOLAR:\n" + "-" * 50 + "\n")

        if student.grades:
            for subject_code, subject_grades in student.grades.items():
                subject = find_subject(subject_code)
                subject_name = subject["name"] if subject else subject_code
                f.write(f"\n{subject_name} [{subject_code}]:\n")

                if subject_grades:
                    subject_avg = statistics.mean(subject_grades.values())
                    f.write(f"  O'rtacha: {subject_avg:.2f}\n")
                    for task, grade in subject_grades.items():
                        f.write(f"  {task}: {grade}\n")
                else:
                    f.write("  Baholar yo'q\n")
        else:
            f.write("Yo'q\n")

        f.write("\n" + "=" * 50 + "\n")

    print(colored(f"✓ Saqlandi: {filename}", "green"))
