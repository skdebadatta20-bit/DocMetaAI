"""Utility helpers for DocMetaAI."""

import os
from typing import Callable

from tkinter import messagebox


def normalize_path(path: str) -> str:
    """Return an absolute normalized path."""
    return os.path.abspath(os.path.expanduser(path))


def safe_execute(action: Callable[[], None], error_message: str) -> None:
    """Execute an action and show a messagebox on error."""
    try:
        action()
    except Exception as error:
        messagebox.showerror("Operation failed", f"{error_message}\n\n{error}")
