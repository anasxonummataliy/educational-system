from functools import wraps
from datetime import datetime
from typing import Callable
from pathlib import Path


def require_role(*allowed_roles):
    def deco(func: Callable):
        @wraps(func)
        def wrapper(session, *args, **kwargs):
            user = getattr(session, "current_user", None)
            if user is None:
                parent = getattr(session, "session", None)
                if parent is not None:
                    user = getattr(parent, "current_user", None)
            if not user or user.role() not in allowed_roles:
                raise PermissionError("Ruxsat yo'q: kerakli rol mavjud emas")
            return func(session, *args, **kwargs)

        return wrapper

    return deco


def log_action(logfile: str = "data/logs.txt"):
    def deco(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                user = None
                if args:
                    session = args[0]
                    user = getattr(session, "current_user", None)
                    if user is None:
                        parent = getattr(session, "session", None)
                        if parent is not None:
                            user = getattr(parent, "current_user", None)
                entry = f"{datetime.now().isoformat()} | {getattr(user, 'username', 'anon')} | {func.__name__}\n"
                Path(logfile).parent.mkdir(parents=True, exist_ok=True)
                with open(logfile, "a", encoding="utf-8") as f:
                    f.write(entry)
                return res
            except Exception:
                raise

        return wrapper

    return deco
