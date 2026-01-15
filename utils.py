import os

from termcolor import colored


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg: str = "Enter bosing..."):
    input(colored(f"\n{msg}", "cyan"))
    clear()


def header(text: str):
    print(colored(f"\n{'='*50}", "magenta"))
    print(colored(text.center(50), "magenta", attrs=["bold"]))
    print(colored(f"{'='*50}\n", "magenta"))
