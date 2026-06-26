"""
CygnussIA Plugin v2
Configuration Manager

Author: CygnussIA Project
License: MIT
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


DEFAULT_CONFIG: Dict[str, Any] = {

    # ===========================
    # Backend
    # ===========================

    "host": "127.0.0.1",
    "port": 8000,

    # ===========================
    # Ollama
    # ===========================

    "ollama_url": "http://127.0.0.1:11434",
    "timeout": 300,
    "stream": True,

    # ===========================
    # Workers
    # ===========================

    "workers": 2,

    # ===========================
    # Cache
    # ===========================

    "cache_enabled": True,
    "cache_size": 4096,

    # ===========================
    # History
    # ===========================

    "history_limit": 1000,

    # ===========================
    # Image
    # ===========================

    "jpeg_quality": 95,
    "png_compression": 3,

    # ===========================
    # Directories
    # ===========================

    "storage": {

        "temp": "storage/temp",

        "cache": "storage/cache",

        "history": "storage/history",

        "thumbs": "storage/thumbnails"

    },

    # ===========================
    # Logs
    # ===========================

    "logs": {

        "folder": "logs",

        "level": "INFO"

    }

}


class Config:

    def __init__(self):

        self.data = DEFAULT_CONFIG.copy()

        self.load()

    def load(self):

        if not CONFIG_FILE.exists():

            self.save()

            return

        try:

            with open(CONFIG_FILE, "r", encoding="utf8") as f:

                user = json.load(f)

            self.merge(self.data, user)

        except Exception:

            self.save()

    def save(self):

        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_FILE, "w", encoding="utf8") as f:

            json.dump(self.data, f, indent=4)

    def merge(self, default, user):

        for key, value in user.items():

            if isinstance(value, dict):

                default.setdefault(key, {})

                self.merge(default[key], value)

            else:

                default[key] = value

    def get(self, key, default=None):

        keys = key.split(".")

        value = self.data

        for k in keys:

            if not isinstance(value, dict):

                return default

            value = value.get(k)

            if value is None:

                return default

        return value

    def set(self, key, value):

        keys = key.split(".")

        ref = self.data

        for k in keys[:-1]:

            ref = ref.setdefault(k, {})

        ref[keys[-1]] = value

        self.save()


config = Config()