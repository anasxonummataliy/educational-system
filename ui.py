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


def authenticate() -> object:
    username = input(colored("Username: ", "cyan")).strip()
    user_rec = find_user(username)
    if not user_rec:
        print(colored("User not found", "red"))
        return None
    password = getpass.getpass(colored("Password: ", "cyan"))
    user_obj = instantiate_user_from_record(user_rec)
    if user_obj and user_obj.authenticate(password):
        session.current_user = user_obj
        print(
            colored(f"Authenticated as {user_obj.username} ({user_obj.role})", "green")
        )
        return user_obj
    print(colored("Authentication failed", "red"))
    return None


def ensure_sample_admin():
    data = load_data()
    if not data.get("users"):
        admin = Admin("admin", "admin")
        add_user(admin)
        print(colored("Created sample admin (admin/admin)", "yellow"))


def run_cli():
    ensure_sample_admin()
    print(colored("Welcome to the Console Educational System", "magenta"))
    while True:
        print(colored("\n1) Login\n2) Exit", "cyan"))
        cmd = input(colored("Choose: ", "cyan")).strip()
        if cmd == "1":
            user = authenticate()
            if user:
                dispatch_menu(user)
        else:
            print(colored("Goodbye", "magenta"))
            break


def dispatch_menu(user):
    if user.role == "Admin":
        admin_menu(user)
    elif user.role == "Teacher":
        teacher_menu(user)
    elif user.role == "Student":
        student_menu(user)


@decorators.require_role("Admin")
@decorators.log_action
def admin_menu(admin: Admin):
    while True:
        print(
            colored(
                "\nAdmin Menu:\n1) Create user\n2) Delete user\n3) Reset password\n4) View logs\n5) Logout",
                "cyan",
            )
        )
        c = input(colored("Choice: ", "cyan")).strip()
        if c == "1":
            uname = input(colored("New username: ", "cyan")).strip()
            r = input(colored("Role (Admin/Teacher/Student): ", "cyan")).strip()
            pwd = getpass.getpass(colored("Password: ", "cyan"))
            if r == "Student":
                u = Student(uname, pwd)
            elif r == "Teacher":
                u = Teacher(uname, pwd)
            else:
                u = Admin(uname, pwd)
            add_user(u)
            print(colored("User created", "green"))
        elif c == "2":
            uname = input(colored("Username to delete: ", "cyan")).strip()
            ok = delete_user(uname)
            print(colored("Deleted" if ok else "Not found", "yellow"))
        elif c == "3":
            uname = input(colored("Username to reset: ", "cyan")).strip()
            new = getpass.getpass(colored("New password: ", "cyan"))
            ok = update_user(uname, {"password": new})
            print(colored("Password updated" if ok else "Not found", "yellow"))
        elif c == "4":
            if os.path.exists("logs.txt"):
                with open("logs.txt") as f:
                    print(colored("\n--- Logs ---", "magenta"))
                    print(f.read())
            else:
                print(colored("No logs yet", "yellow"))
        else:
            session.current_user = None
            break


@decorators.require_role("Teacher")
@decorators.log_action
def teacher_menu(teacher: Teacher):
    while True:
        print(
            colored(
                "\nTeacher Menu:\n1) Record attendance\n2) Record grade\n3) Class analytics\n4) Logout",
                "cyan",
            )
        )
        c = input(colored("Choice: ", "cyan")).strip()
        if c == "1":
            sname = input(colored("Student username: ", "cyan")).strip()
            rec = find_user(sname)
            if not rec:
                print(colored("Student not found", "red"))
                continue
            student = instantiate_user_from_record(rec)
            teacher.record_attendance(student)
            update_user(sname, {"attendance": student._attendance})
            print(colored("Attendance recorded", "green"))
        elif c == "2":
            sname = input(colored("Student username: ", "cyan")).strip()
            rec = find_user(sname)
            if not rec:
                print(colored("Student not found", "red"))
                continue
            student = instantiate_user_from_record(rec)
            asg = input(colored("Assignment name: ", "cyan")).strip()
            try:
                g = float(input(colored("Grade: ", "cyan")).strip())
            except ValueError:
                print(colored("Invalid grade", "red"))
                continue
            teacher.record_grade(student, asg, g)
            update_user(sname, {"grades": student._grades})
            print(colored("Grade recorded", "green"))
        elif c == "3":
            users = [
                instantiate_user_from_record(u)
                for u in list_users()
                if u["role"] == "Student"
            ]
            res = teacher.analyze_class(users)
            print(colored("Class analytics:", "magenta"))
            print(res)
            with open("reports_class.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["metric", "value"])
                for k, v in res.items():
                    writer.writerow([k, v])
            print(colored("Saved reports_class.csv", "green"))
        else:
            session.current_user = None
            break


@decorators.require_role("Student")
@decorators.log_action
def student_menu(student: Student):
    while True:
        print(
            colored(
                "\nStudent Menu:\n1) View progress\n2) View attendance\n3) Export progress\n4) Logout",
                "cyan",
            )
        )
        c = input(colored("Choose: ", "cyan")).strip()
        if c == "1":
            p = student.view_progress()
            print(p)
        elif c == "2":
            print(student.view_attendance())
        elif c == "3":
            fname = f"report_{student.username}.txt"
            with open(fname, "w") as f:
                f.write(
                    f"Student: {student.username}\nAverage: {student.average}\nGrades:\n"
                )
                for k, v in student.grades.items():
                    f.write(f"{k}: {v}\n")
            print(colored("Exported " + fname, "green"))
        else:
            session.current_user = None
            break
