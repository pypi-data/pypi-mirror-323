"""Common methods for psiutils."""
from pathlib import Path
import tkinter as tk
import ctypes
from typing import Any
import platform

import psiutils.text as text


def display_icon(root: tk.Tk, icon_file_path: str,
                 ignore_error: bool = True) -> None:
    if platform.system() == 'Windows':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('_')
    try:
        icon = tk.PhotoImage(master=root, file=icon_file_path)
        root.wm_iconphoto(True, icon)
    except tk.TclError as err:
        if ignore_error and text.NO_SUCH_FILE in str(err):
            return
        print(f'Cannot find icon file: {icon_file_path}')


class Enum():
    def __init__(self, values: dict) -> None:
        self.values = invert(values)


def confirm_delete(parent: Any) -> str:
    question = text.DELETE_THESE_ITEMS
    return tk.messagebox.askquestion(
        'Delete items', question, icon='warning', parent=parent)


def create_directories(path: str | Path) -> bool:
    """Create directories recursively."""
    print('*** pathlib.Path(path).mkdir(parents=True, exist_ok=True) ***')
    create_parts = []
    create_path = Path(path)
    for part in create_path.parts:
        create_parts.append(part)
        new_path = Path(*create_parts)
        if not Path(new_path).is_dir():
            try:
                Path(new_path).mkdir()
            except PermissionError:
                print(f'Invalid file path: {new_path}')
                return False
    return True


def invert(enum: dict) -> dict:
    """Add the inverse items to a dictionary."""
    output = {}
    for key, item in enum.items():
        output[key] = item
        output[item] = key
    return output


def enable_frame(parent: tk.Frame, enable: bool = True) -> None:
    state = tk.NORMAL if enable else tk.DISABLED
    for child in parent.winfo_children():
        w_type = child.winfo_class()
        if w_type in ('Frame', 'Labelframe', 'TFrame', 'TLabelframe'):
            enable_frame(child, enable)
        else:
            child.configure(state=state)
