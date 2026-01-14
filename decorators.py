import functools
import datetime
import session

LOG_FILE = "logs.txt"


def _append_log(entry: str):
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


def log_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = getattr(session, "current_user", None)
        username = user.username if user else "anonymous"
        entry = f"{datetime.datetime.now().isoformat()} | {username} | {func.__name__} | args={args} kwargs={kwargs}"
        _append_log(entry)
        return func(*args, **kwargs)

    return wrapper


def require_role(*allowed_roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = getattr(session, "current_user", None)
            if not user:
                raise PermissionError("Authentication required")
            if user.role not in allowed_roles:
                raise PermissionError(
                    f"Role {user.role} not allowed for this action. Required: {allowed_roles}"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
