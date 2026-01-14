from ui import ConsoleUI
from storage import Storage


def main():
    storage = Storage()
    ui = ConsoleUI(storage)
    ui.run()


if __name__ == "__main__":
    main()
