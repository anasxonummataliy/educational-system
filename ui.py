from termcolor import colored
from models import Admin, Teacher, Student
from decorators import require_role, log_action
from typing import Dict
from dataclasses import dataclass


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
                print(colored('\nGoodbye.', 'cyan'))
                break
            except Exception as e:
                print(colored(f'Error: {e}', 'red'))

    def show_welcome(self):
        print(colored('=== University Student Management ===', 'green'))

    def login(self) -> bool:
        users = self.storage.list_users()
        print(colored('Login (or type exit):', 'yellow'))
        uname = input('username: ').strip()
        if uname.lower() in ('exit', 'quit'):
            return False
        pwd = input('password: ').strip()
        u = users.get(uname)
        if not u or not u.check_password(pwd):
            print(colored('Invalid credentials', 'red'))
            return True
        self.session.current_user = u
        print(colored(f'Welcome {u.username} ({u.role()})', 'cyan'))
        return True

    def route(self):
        role = self.session.current_user.role()
        if role == 'admin':
            self.admin_menu()
        elif role == 'teacher':
            self.teacher_menu()
        elif role == 'student':
            self.student_menu()

    @log_action()
    @require_role('admin')
    def admin_menu(self, session):
        while True:
            print(colored('\nAdmin Menu: 1) Add User 2) Remove User 3) List Users 4) Logout', 'yellow'))
            cmd = input('> ').strip()
            if cmd == '1':
                self._add_user()
            elif cmd == '2':
                self._remove_user()
            elif cmd == '3':
                self._list_users()
            elif cmd == '4':
                self.session.current_user = None
                break

    def _add_user(self):
        uname = input('new username: ').strip()
        pwd = input('password: ').strip()
        typ = input('type (admin/teacher/student): ').strip()
        if typ == 'admin':
            u = Admin(uname, pwd)
        elif typ == 'teacher':
            u = Teacher(uname, pwd)
        else:
            u = Student(uname, pwd)
        self.storage.add_user(u)
        print(colored('User added', 'green'))

    def _remove_user(self):
        uname = input('username to remove: ').strip()
        ok = self.storage.remove_user(uname)
        print(colored('Removed' if ok else 'Not found', 'green' if ok else 'red'))

    def _list_users(self):
        users = self.storage.list_users()
        for u in users.values():
            print(f'- {u.username} ({u.role()})')

    @log_action()
    @require_role('teacher')
    def teacher_menu(self, session):
        while True:
            print(colored('\nTeacher Menu: 1) Mark Attendance 2) Add Grade 3) Student Report 4) Logout', 'yellow'))
            cmd = input('> ').strip()
            if cmd == '1':
                self._mark_attendance()
            elif cmd == '2':
                self._add_grade()
            elif cmd == '3':
                self._student_report()
            elif cmd == '4':
                self.session.current_user = None
                break

    def _find_student(self, username: str):
        users = self.storage.list_users()
        u = users.get(username)
        if not u or not isinstance(u, Student):
            print(colored('Student not found', 'red'))
            return None
        return u

    def _mark_attendance(self):
        uname = input('student username: ').strip()
        s = self._find_student(uname)
        if not s:
            return
        val = input('present? (y/n): ').strip().lower() in ('y', 'yes')
        s.add_attendance(val)
        users = self.storage.list_users()
        users[s.username] = s
        self.storage.save_users(users)
        print(colored('Attendance recorded', 'green'))

    def _add_grade(self):
        uname = input('student username: ').strip()
        s = self._find_student(uname)
        if not s:
            return
        try:
            g = float(input('grade (0-100): ').strip())
        except ValueError:
            print(colored('Invalid grade', 'red'))
            return
        s.add_grade(g)
        users = self.storage.list_users()
        users[s.username] = s
        self.storage.save_users(users)
        print(colored('Grade added', 'green'))

    @log_action()
    def _student_report(self):
        uname = input('student username: ').strip()
        s = self._find_student(uname)
        if not s:
            return
        print(colored(f"Report for {s.username}", 'cyan'))
        print('Average:', colored(f"{:.2f}".format(s.average), 'magenta'))
        print('Attendance records:', len(s.attendance))
        if s.at_risk():
            print(colored('Academic Risk: YES', 'red'))
        else:
            print(colored('Academic Risk: NO', 'green'))

    @log_action()
    @require_role('student')
    def student_menu(self, session):
        s = self.session.current_user
        while True:
            print(colored('\nStudent Menu: 1) View Progress 2) Logout', 'yellow'))
            cmd = input('> ').strip()
            if cmd == '1':
                self._view_progress(s)
            elif cmd == '2':
                self.session.current_user = None
                break

    def _view_progress(self, s: Student):
        print(colored(f"Student: {s.username}", 'cyan'))
        print('Average:', colored(f"{:.2f}".format(s.average), 'magenta'))
        print('Grades:', ', '.join(str(g) for g in s.grades) or 'none')
        print('Attendance records:', len(s.attendance))
        if s.at_risk():
            print(colored('You are at academic risk. Please contact advisor.', 'red'))
