from termcolor import colored


def draw_box(matn: str, rang="green"):
    kengligi = 60
    chiziq = "─" * kengligi
    print(f"\n{colored(f'┌{chiziq}┐', rang)}")
    print(colored(f"  {matn.center(kengligi)}  ", rang, attrs=["bold"]))
    print(colored(f"└{chiziq}┘", rang))
