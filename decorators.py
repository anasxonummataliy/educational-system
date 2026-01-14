import functools


def log_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        with open("system_logs.txt", "a") as f:
            f.write(f"Action: {func.__name__} executed.\n")
        return result

    return wrapper


def require_role(role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(user, *args, **kwargs):
            if user.role == role:
                return func(user, *args, **kwargs)
            else:
                print(f"Ruxsat berilmadi! Ushbu amal faqat {role} uchun.")

        return wrapper

    return decorator
