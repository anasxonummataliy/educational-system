import logging
import session

logger = logging.getLogger("educational")


def log_action(func):
    def wrapper(*args, **kwargs):
        user = getattr(session, "current_user")
        username = user.username if user else "anonim"
        logger.info(f"{username} - {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


def require_role(*allowed_roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = getattr(session, "current_user")
            if not user:
                raise PermissionError("Tizimga kirish talab qilinadi")
            if user.role not in allowed_roles:
                raise PermissionError(f"Ruxsat yo'q. Kerak: {allowed_roles}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
