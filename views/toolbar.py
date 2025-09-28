from __future__ import annotations

import customtkinter as ctk
from typing import Callable, Optional

from resource.colors import PRIMARY_BLUE, WHITE, BLACK, GRAY
from resource.icons import get_icon
from resource.fonts import FONT_HUGE, WEIGHT_BOLD


class Toolbar(ctk.CTkFrame):
    """Reusable header bar with configurable title and actions.

    - set_title(text): update main title
    - configure_buttons: set callbacks or hide buttons
    - update_admin_visibility(user): show/hide tools button based on role
    """

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        *,
        title: str = "",
        on_go_subir: Optional[Callable[[], None]] = None,
        on_go_chat: Optional[Callable[[], None]] = None,
        on_go_config: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(master, fg_color=PRIMARY_BLUE, corner_radius=0)
        # Grid config
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # Enforce consistent height across views (slightly larger)
        _btn_size = 52
        _pad_x = 10
        _pad_y = 12
        try:
            self.configure(height=_btn_size + 2 * _pad_y)
            # Prevent the grid from resizing the frame height based on children
            self.grid_propagate(False)
        except Exception:
            pass

        # Left controls
        self.left_controls = ctk.CTkFrame(self, fg_color=PRIMARY_BLUE, corner_radius=0)
        self.left_controls.grid(row=0, column=0, sticky="nsw", padx=_pad_x, pady=0)
        try:
            self.left_controls.grid_rowconfigure(0, weight=1)
        except Exception:
            pass

        # Right controls
        self.right_controls = ctk.CTkFrame(self, fg_color=PRIMARY_BLUE, corner_radius=0)
        self.right_controls.grid(row=0, column=2, sticky="nse", padx=_pad_x, pady=0)
        try:
            self.right_controls.grid_rowconfigure(0, weight=1)
        except Exception:
            pass
        self.btn_subir = ctk.CTkButton(
            self.left_controls,
            text="",
            width=_btn_size,
            height=_btn_size,
            font=ctk.CTkFont(size=20),
            corner_radius=25,
            fg_color=WHITE,
            text_color=BLACK,
            hover_color=GRAY,
            image=get_icon("update", size=(28, 28)),
            command=on_go_subir or (lambda: None),
        )
        self.btn_subir.grid(row=0, column=0, padx=(0, 8), pady=_pad_y)

        self.btn_herramientas = ctk.CTkButton(
            self.left_controls,
            text="",
            width=_btn_size,
            height=_btn_size,
            font=ctk.CTkFont(size=20),
            corner_radius=25,
            fg_color=WHITE,
            text_color=BLACK,
            hover_color=GRAY,
            image=get_icon("settings", size=(28, 28)),
            command=on_go_config or (lambda: None),
        )
        self.btn_herramientas.grid(row=0, column=1, pady=_pad_y)

        self.btn_chat = ctk.CTkButton(
            self.right_controls,
            text="",
            width=_btn_size,
            height=_btn_size,
            font=ctk.CTkFont(size=20),
            corner_radius=25,
            fg_color=WHITE,
            text_color=BLACK,
            hover_color=GRAY,
            image=get_icon("chat", size=(28, 28)),
            command=on_go_chat or (lambda: None),
        )
        self.btn_chat.grid(row=0, column=0, pady=_pad_y)

        # Title centered
        self._title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=FONT_HUGE, weight=WEIGHT_BOLD),
            text_color=WHITE,
        )
        self._title_label.grid(row=0, column=1, sticky="nsew")

        # Store callbacks
        self._on_go_subir = on_go_subir
        self._on_go_chat = on_go_chat
        self._on_go_config = on_go_config

    # --- Public API ---
    def set_title(self, text: str) -> None:
        """Update header title text."""
        try:
            self._title_label.configure(text=text)
        except Exception:
            pass

    def configure_buttons(
        self,
        *,
        on_go_subir: Optional[Callable[[], None]] = None,
        on_go_chat: Optional[Callable[[], None]] = None,
        on_go_config: Optional[Callable[[], None]] = None,
        show_subir: Optional[bool] = None,
        show_chat: Optional[bool] = None,
        show_config: Optional[bool] = None,
    ) -> None:
        """Configure callbacks and visibility for buttons."""
        if on_go_subir is not None:
            self.btn_subir.configure(command=on_go_subir)
        if on_go_chat is not None:
            self.btn_chat.configure(command=on_go_chat)
        if on_go_config is not None:
            self.btn_herramientas.configure(command=on_go_config)

        if show_subir is not None:
            (self.btn_subir.grid if show_subir else self.btn_subir.grid_remove)()
        if show_chat is not None:
            (self.btn_chat.grid if show_chat else self.btn_chat.grid_remove)()
        if show_config is not None:
            (
                self.btn_herramientas.grid
                if show_config
                else self.btn_herramientas.grid_remove
            )()

    def update_admin_visibility(self, user: Optional[dict]) -> None:
        """Show/hide tools button based on user role."""
        try:
            es_admin = bool(user and (user.get("tipo") or "user") == "admin")
            if es_admin:
                self.btn_herramientas.grid()
            else:
                self.btn_herramientas.grid_remove()
        except Exception:
            # Hide by default on error
            try:
                self.btn_herramientas.grid_remove()
            except Exception:
                pass
