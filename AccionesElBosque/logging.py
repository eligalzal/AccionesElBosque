from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime:s} {name} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "{levelname} {asctime:s} {name} {module}.py (line {lineno:d}) {funcName} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": BASE_DIR / "django.log",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
            "formatter": "json",
        },
    },
    "loggers": {
        "": {
            "level": "WARNING",
            "handlers": ["console", "file", "mail_admins"],
        },
        "django": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.template": {
            "level": "DEBUG",
            "handlers": ["file"],
            "propagate": False,
        },
    },
    "loggers": {
        "": {
            "level": "WARNING",
            "handlers": ["console", "file", "mail_admins"],
        },
        "django": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.template": {
            "level": "DEBUG",
            "handlers": ["file"],
            "propagate": False,
        },
    },
}