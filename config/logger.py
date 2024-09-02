# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger("llmserver2")

def initialize_logging_config(log_path: str):
    """
    初始化日志配置
    """
    from pathlib import Path

    log_path = log_path.rstrip('/')

    dir_path = Path(log_path)
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
    elif not dir_path.is_dir():
        dir_path.unlink()
        dir_path.mkdir(parents=True, exist_ok=True)
    return {
        'version': 1,
        'loggers': {
            "llmserver2": {"level": "INFO", "handlers": ["info-file"]},
            "llmserver2.error": {"level": "INFO", "handlers": ["error-file"]},
            "uvicorn": {"level": "INFO", "handlers": ["info-file"]},
            "uvicorn.error": {"level": "ERROR", "handlers": ["error-file"], "propagate" : False},
            "uvicorn.acces": {"level": "INFO", "handlers": ["access-file"], "propagate" : False}
        },
        'handlers': {
            "info-file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "generic",
                "when": "midnight",
                "backupCount": 30,
                "filename": f"{log_path}/llminf.log"
            },
            "error-file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "generic",
                "when": "midnight",
                "backupCount": 30,
                "filename": f"{log_path}/llmerr.log"
            },
            "access-file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "uvicorn.access",
                "when": "midnight",
                "backupCount": 30,
                "filename": f"{log_path}/llmacc.log"
            }
        },
        'formatters': {
            "generic": {
                "format": "[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] [Line:%(lineno)d] %(message)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S]",
                "class": "logging.Formatter",
            },
            "uvicorn.access" : {
                "format": "%(levelprefix)s %(host)s - [%(asctime)s] %(request_line)s %(status_code)s",
                "datefmt": "[%Y-%m-%d %H:%M:%S]",
                "class": "logging.Formatter",
            }
        },
    }
