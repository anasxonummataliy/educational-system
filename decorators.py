import functools
import logging
import session

logger = logging.getLogger("educational")


def log_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = getattr(session, "current_user", None)
        username = user.username if user else "anonim"
        msg = f"Foydalanuvchi: {username} | Amal: {func.__name__} | args={args} kwargs={kwargs}"
        logger.info(msg)
        return func(*args, **kwargs)

    return wrapper


def require_role(*allowed_roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = getattr(session, "current_user", None)
            if not user:
                raise PermissionError("Tizimga kirish talab qilinadi")
            if user.role not in allowed_roles:
                raise PermissionError(f"Rol ruxsati yo'q. Kerak: {allowed_roles}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
