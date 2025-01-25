import asyncio
import ctypes
import tkinter as tk
from tkinter import filedialog
from starlette.responses import JSONResponse
import threading
import time
import os
from typing import Literal

dialog_should_close = threading.Event()

def set_dpi_awareness():
    if os.name == "nt":
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

def open_file_dialog_sync(mode: Literal["file", "folder"]):
    set_dpi_awareness()

    root = tk.Tk()
    root.iconify()
    
    if mode == "file":
        paths = filedialog.askopenfilenames()
    elif mode == "folder":
        paths = filedialog.askdirectory()
    root.destroy()

    if paths:
        return paths
    else:
        print("No file selected.")
        return ()

async def choose_file_on_server():
    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(None, open_file_dialog_sync, "file")
    return JSONResponse(content={"path": path})

async def choose_folder_on_server():
    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(None, open_file_dialog_sync, "folder")
    return JSONResponse(content={"path": path})