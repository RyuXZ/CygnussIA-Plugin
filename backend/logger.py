"""
CygnussIA Plugin v2
Professional Logger

Author: CygnussIA Project
License: MIT
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config import config


class LoggerManager:
    """
    Configura un sistema de logging profesional.

    Características:

    • Consola con formato legible
    • plugin.log
    • error.log
    • Rotación automática
    • Singleton
    """

    def __init__(self):

        self.initialized = False

        self.logs_folder = Path(
            config.get("logs.folder", "logs")
        )

        self.logs_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    def initialize(self):

        if self.initialized:
            return

        level_name = config.get(
            "logs.level",
            "INFO"
        ).upper()

        level = getattr(
            logging,
            level_name,
            logging.INFO
        )

        root = logging.getLogger()

        root.setLevel(level)

        formatter = logging.Formatter(

            "[%(asctime)s]"
            " [%(levelname)s]"
            " [%(name)s]"
            " %(message)s",

            "%Y-%m-%d %H:%M:%S"

        )

        console = logging.StreamHandler()

        console.setFormatter(formatter)

        console.setLevel(level)

        plugin_handler = RotatingFileHandler(

            self.logs_folder / "plugin.log",

            maxBytes=10 * 1024 * 1024,

            backupCount=5,

            encoding="utf8"

        )

        plugin_handler.setFormatter(formatter)

        plugin_handler.setLevel(level)

        error_handler = RotatingFileHandler(

            self.logs_folder / "error.log",

            maxBytes=10 * 1024 * 1024,

            backupCount=10,

            encoding="utf8"

        )

        error_handler.setFormatter(formatter)

        error_handler.setLevel(logging.ERROR)

        root.addHandler(console)
        root.addHandler(plugin_handler)
        root.addHandler(error_handler)

        self.initialized = True

        logging.getLogger("CygnussIA").info(
            "Logger initialized."
        )

    def get_logger(
        self,
        name: Optional[str] = None
    ) -> logging.Logger:

        if not self.initialized:
            self.initialize()

        return logging.getLogger(name)


logger_manager = LoggerManager()


def get_logger(name: str):

    return logger_manager.get_logger(name)