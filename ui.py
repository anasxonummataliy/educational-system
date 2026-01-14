import os
from storage import save_data



def admin_menu(system, user):
    while True:
        user.display_menu()
        choice = input("Tanlov: ")
        if choice == "1":
            uid = input("Yangi User ID: ")
            name = input("Ism: ")
            role = input("Rol (Student/Teacher): ")
            pwd = input("Parol: ")
            from models import Student, Teacher

            new_user = (
                Student(uid, name, pwd)
                if role.lower() == "student"
                else Teacher(uid, name, pwd)
            )
            system.users.append(new_user)
            save_data(system.users)
            print("Foydalanuvchi qo'shildi!")
        elif choice == "3":
            if os.path.exists("system_logs.txt"):
                with open("system_logs.txt", "r") as f:
                    print(f.read())
            else:
                print("Loglar mavjud emas.")
        elif choice == "4":
            break


def teacher_menu(system, user):
    while True:
        user.display_menu()
        choice = input("Tanlov: ")
        if choice == "2":  # Assign Grade
            sid = input("Talaba ID sini kiriting: ")
            subject = input("Fan nomi: ")
            try:
                grade = int(input("Baho (0-100): "))
                for u in system.users:
                    if u.user_id == sid and u.role == "Student":
                        u.grades[subject] = grade
                        save_data(system.users)
                        print("Baho saqlandi.")
            except ValueError:
                print("Xato: Raqam kiriting!")
        elif choice == "4":
            break


def student_menu(user):
    while True:
        user.display_menu()
        choice = input("Tanlov: ")
        if choice == "1":
            print(f"\nSizning baholaringiz: {user.grades}")
            if user.grades:
                avg = sum(user.grades.values()) / len(user.grades)
                print(f"O'rtacha baho: {avg}")
        elif choice == "3":
            break
