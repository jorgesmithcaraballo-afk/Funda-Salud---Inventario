import customtkinter as ctk
from typing import Optional
from resource.colors import WHITE
from resource.sizes import MODAL_WIDTH, MODAL_HEIGHT, MODAL_PADDING


def create_modal(
    parent: ctk.CTkFrame,
    title: str,
    transient: Optional[ctk.CTkToplevel] = None,
) -> tuple[ctk.CTkToplevel, ctk.CTkFrame]:
    """Crea un modal estándar con fondo blanco y padding, devuelve content match_parent."""
    win = ctk.CTkToplevel(parent)
    win.title(title)
    win.configure(fg_color=WHITE)
    try:
        win.geometry(f"{MODAL_WIDTH}x{MODAL_HEIGHT}")
        win.resizable(True, True)
    except Exception:
        pass
    try:
        win.transient(transient or parent.winfo_toplevel())
        win.grab_set()
    except Exception:
        pass

    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)
    win.geometry(f"{MODAL_WIDTH}x{MODAL_HEIGHT}")
    win.resizable(False, False)

    container = ctk.CTkFrame(win, fg_color=WHITE)
    container.grid(row=0, column=0, sticky="nsew")
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    # 🔹 content dinámico
    content = ctk.CTkFrame(container, fg_color="transparent")
    content.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
    # content.grid_rowconfigure(0, weight=1)
    content.grid_columnconfigure(0, weight=1)

    return win, content
