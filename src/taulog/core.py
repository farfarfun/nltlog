import sys
from functools import cache
from pathlib import Path

from loguru import logger

_DEFAULT_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} |{level:8}| "
    "{name} : {module}:{line:4} | {extra[module_name]} | - {message}"
)
_DEFAULT_FORMAT_COLOR = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} |<lvl>{level:8}</>| "
    "{name} : {module}:{line:4} | <cyan>{extra[module_name]}</> | - <lvl>{message}</>"
)


def _ensure_log_dir(log_dir: str = "logs") -> Path:
    """Ensure log directory exists with a .gitignore file."""
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    gitignore = path / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*")
    return path


def _configure_default_handlers(log_dir: str = "logs") -> None:
    """Configure global logger handlers."""
    _ensure_log_dir(log_dir)
    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "format": _DEFAULT_FORMAT_COLOR,
                "colorize": True,
                "level": "INFO",
            },
            {
                "sink": f"{log_dir}/all.log",
                "format": _DEFAULT_FORMAT,
                "colorize": False,
                "rotation": "00:00",
                "compression": "gz",
                "retention": 30,
                "level": "INFO",
            },
        ]
    )


_configure_default_handlers()


@cache
def get_logger(
    name: str = "default",
    level: str = "INFO",
    formatter: str | None = None,
):
    """Get a named logger with its own log file.

    Results are cached — subsequent calls with the same arguments
    return the same logger instance without adding duplicate handlers.
    """
    _ensure_log_dir()
    logger.add(
        sink=f"logs/{name}.log",
        format=formatter or _DEFAULT_FORMAT,
        filter=lambda record, _name=name: record["extra"].get("module_name") == _name,
        level=level,
        rotation="00:00",
        compression="gz",
        retention=7,
        colorize=False,
    )
    return logger.bind(module_name=name)


# Backward-compatible alias
getLogger = get_logger
