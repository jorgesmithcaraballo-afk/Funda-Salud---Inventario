import customtkinter as ctk
from tkinter import messagebox
from services.application.configuracion_service import ConfiguracionService
from resource.colors import (
    WHITE,
    TABLE_ROW_ALT_BG,
    TEXT_DARK,
    TEXT_MUTED,
    ERROR_TEXT_RED,
    GRAY,
    DARK_GRAY,
    SECONDARY_BLUE,
    SECONDARY_BLUE_HOVER,
    get_content_button_style,
)
from resource.sizes import ENTRY_HEIGHT, CONTENT_SELECT_HEIGHT, CONTENT_SELECT_WIDTH
from .modal_factory import create_modal
from resource.strings import (
    AGREGAR_USUARIO,
    NUEVO_USUARIO,
    COMPLETAR_DATOS_NUEVO_USUARIO,
    NOMBRE,
    APELLIDO,
    CONTRASENA,
    CONFIRMAR_CONTRASENA,
    TIPO,
    CANCELAR,
    GUARDAR,
)


def open_add_user_modal(view) -> None:
    """Modal 'Agregar usuario'."""

    if (
        hasattr(view, "_add_user_win")
        and view._add_user_win is not None
        and view._add_user_win.winfo_exists()
    ):
        try:
            view._add_user_win.focus_set()
        except Exception:
            pass
        return

    win, content = create_modal(view, AGREGAR_USUARIO)
    view._add_user_win = win

    # Header
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.grid(row=0, column=0, pady=(10, 20), sticky="ew")
    header.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(
        header,
        text=NUEVO_USUARIO,
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=TEXT_DARK,
    ).grid(row=0, column=0, sticky="n", pady=(0, 4))
    ctk.CTkLabel(
        header,
        text=COMPLETAR_DATOS_NUEVO_USUARIO,
        font=ctk.CTkFont(size=14),
        text_color=TEXT_MUTED,
    ).grid(row=1, column=0, sticky="n")

    # Variables
    view._nombre_var = ctk.StringVar()
    view._apellido_var = ctk.StringVar()
    view._contrasena_var = ctk.StringVar()
    view._contrasena2_var = ctk.StringVar()
    view._tipo_var = ctk.StringVar(value="user")

    fields = [
        (NOMBRE, view._nombre_var, None),
        (APELLIDO, view._apellido_var, None),
        (CONTRASENA, view._contrasena_var, "*"),
        (CONFIRMAR_CONTRASENA, view._contrasena2_var, "*"),
        (TIPO, view._tipo_var, "option"),
    ]

    for i, (label_text, var, show) in enumerate(fields, start=1):
        bg_color = WHITE if i % 2 == 0 else TABLE_ROW_ALT_BG
        row_frame = ctk.CTkFrame(content, fg_color=bg_color, corner_radius=6)
        row_frame.grid(row=i, column=0, sticky="ew", pady=4, padx=2, ipadx=4, ipady=4)
        row_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row_frame, text=label_text, anchor="w", width=120).grid(
            row=0, column=0, padx=(8, 12)
        )
        if show == "option":
            ctk.CTkOptionMenu(
                row_frame,
                variable=var,
                values=["admin", "user"],
                width=CONTENT_SELECT_WIDTH,
                height=CONTENT_SELECT_HEIGHT,
            ).grid(row=0, column=1, sticky="ew", padx=(0, 8))
        else:
            ctk.CTkEntry(
                row_frame,
                textvariable=var,
                height=ENTRY_HEIGHT,
                show=show if show else None,
            ).grid(row=0, column=1, sticky="ew", padx=(0, 8))

    # Error label
    view._error_label = ctk.CTkLabel(content, text="", text_color=ERROR_TEXT_RED)
    view._error_label.grid(row=len(fields) + 1, column=0, sticky="ew", pady=(8, 0))

    # Footer
    btns = ctk.CTkFrame(content, fg_color="transparent")
    btns.grid(row=len(fields) + 2, column=0, sticky="e", pady=20, padx=10)
    base = get_content_button_style()
    # Usar constantes globales para colores (Opción B)
    cancel = {**base, "fg_color": GRAY, "hover_color": DARK_GRAY}
    save = {**base, "fg_color": SECONDARY_BLUE, "hover_color": SECONDARY_BLUE_HOVER}

    ctk.CTkButton(btns, text=CANCELAR, command=win.destroy, **cancel).grid(
        row=0, column=1, padx=(8, 0)
    )
    view._save_btn = ctk.CTkButton(
        btns, text=GUARDAR, command=view._save_new_user, **save
    )
    view._save_btn.grid(row=0, column=0)
