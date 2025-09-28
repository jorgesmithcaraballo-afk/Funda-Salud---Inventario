import threading
from typing import Dict, Any

import customtkinter as ctk
from tkinter import messagebox

from services.application.configuracion_service import ConfiguracionService
from resource.colors import get_content_button_style, ERROR_TEXT_RED
from resource.sizes import ENTRY_HEIGHT, CONTENT_SELECT_WIDTH, CONTENT_SELECT_HEIGHT
from .modal_factory import create_modal
from resource.strings import (
    EDITAR,
    USUARIO,
    NOMBRE,
    APELLIDO,
    NUEVA_CONTRASEÑA,
    TIPO,
    CANCELAR,
    GUARDAR,
)


def open_edit_user_modal(view, row: Dict[str, Any]) -> None:
    """Open modal to edit a user.
    If the user is 'naila', the type cannot be changed.
    """
    win, container = create_modal(view, f"{EDITAR} {USUARIO} #{row.get('id')}")
    # Ensure window is properly destroyed when closed via OS window controls
    try:
        win.protocol("WM_DELETE_WINDOW", win.destroy)
    except Exception:
        pass

    # Variables de entrada
    nombre_var = ctk.StringVar(value=row.get("nombre") or "")
    apellido_var = ctk.StringVar(value=row.get("apellido") or "")
    contrasena_var = ctk.StringVar(value="")
    tipo_var = ctk.StringVar(value=row.get("tipo") or "user")
    is_naila = (row.get("nombre") or "").strip().lower() == "naila"

    # -------------------------------
    # Campos de formulario
    # -------------------------------
    # Form fields (avoid inline grid to keep widget references alive)
    name_label = ctk.CTkLabel(
        container, text=NOMBRE, font=ctk.CTkFont(size=14, weight="bold")
    )
    name_label.grid(row=0, column=0, sticky="w", pady=(5, 0), padx=10)
    name_entry = ctk.CTkEntry(container, textvariable=nombre_var, height=ENTRY_HEIGHT)
    name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

    last_label = ctk.CTkLabel(
        container, text=APELLIDO, font=ctk.CTkFont(size=14, weight="bold")
    )
    last_label.grid(row=2, column=0, sticky="w", pady=(5, 0), padx=10)
    last_entry = ctk.CTkEntry(container, textvariable=apellido_var, height=ENTRY_HEIGHT)
    last_entry.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

    pass_label = ctk.CTkLabel(
        container, text=NUEVA_CONTRASEÑA, font=ctk.CTkFont(size=14, weight="bold")
    )
    pass_label.grid(row=4, column=0, sticky="w", pady=(5, 0), padx=10)
    pass_entry = ctk.CTkEntry(
        container, textvariable=contrasena_var, show="*", height=ENTRY_HEIGHT
    )
    pass_entry.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

    type_label = ctk.CTkLabel(
        container, text=TIPO, font=ctk.CTkFont(size=14, weight="bold")
    )
    type_label.grid(row=6, column=0, sticky="w", pady=(5, 0), padx=10)
    if is_naila:
        type_value_label = ctk.CTkLabel(container, text=row.get("tipo") or "user")
        type_value_label.grid(row=7, column=0, columnspan=2, sticky="w", padx=10)
    else:
        type_menu = ctk.CTkOptionMenu(
            container,
            variable=tipo_var,
            values=["admin", "user"],
            width=CONTENT_SELECT_WIDTH,
            height=CONTENT_SELECT_HEIGHT,
        )
        type_menu.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10)

    # -------------------------------
    # Label de errores
    # -------------------------------
    error_label = ctk.CTkLabel(container, text="", text_color=ERROR_TEXT_RED)
    error_label.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))

    # -------------------------------
    # Validación
    # -------------------------------
    def validate() -> bool:
        if not (nombre_var.get() or "").strip():
            error_label.configure(text="Nombre es obligatorio")
            return False
        if not (apellido_var.get() or "").strip():
            error_label.configure(text="Apellido es obligatorio")
            return False
        if not is_naila:
            t = (tipo_var.get() or "").strip().lower()
            if t not in ("admin", "user"):
                error_label.configure(text="Tipo inválido")
                return False
        if (contrasena_var.get() or "") and not (5 <= len(contrasena_var.get()) <= 8):
            error_label.configure(
                text="La nueva contraseña debe tener entre 5 y 8 caracteres"
            )
            return False
        error_label.configure(text="")
        return True

    # -------------------------------
    # Guardar cambios
    # -------------------------------
    def save_changes() -> None:
        if not validate():
            return
        nombre = nombre_var.get().strip()
        apellido = apellido_var.get().strip()
        npass = (contrasena_var.get() or "").strip()
        tipo = (row.get("tipo") or "user") if is_naila else (tipo_var.get() or "user")
        tipo = (tipo or "user").strip().lower()

        def worker() -> None:
            try:
                if npass:
                    ConfiguracionService.update_user(
                        user_id=row.get("id"),
                        nombre=nombre,
                        apellido=apellido,
                        tipo=tipo,
                        nueva_contra=npass,
                    )
                else:
                    ConfiguracionService.update_user(
                        user_id=row.get("id"),
                        nombre=nombre,
                        apellido=apellido,
                        tipo=tipo,
                    )
                view.after(
                    0, lambda: messagebox.showinfo("Usuario", "Cambios guardados")
                )
                view.after(0, win.destroy)
                # Safely refresh users list if the view provides a suitable callback
                try:
                    if hasattr(view, "_load_users_list") and callable(
                        view._load_users_list
                    ):
                        view.after(0, view._load_users_list)
                except Exception:
                    pass
            except Exception as e:
                view._logger.error(f"Error guardando cambios: {e}")
                view.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"No se pudo guardar cambios:\n{e}"
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()

    # -------------------------------
    # Footer con botones
    # -------------------------------
    footer = ctk.CTkFrame(container, fg_color="transparent")
    footer.grid(row=9, column=0, columnspan=2, sticky="s", pady=12)
    footer.grid_columnconfigure((0, 1), weight=1)

    base = get_content_button_style()
    cancel_btn = ctk.CTkButton(footer, text=CANCELAR, command=win.destroy, **base)
    cancel_btn.grid(row=0, column=0, padx=5, sticky="se")

    save_btn = ctk.CTkButton(footer, text=GUARDAR, command=save_changes, **base)
    save_btn.grid(row=0, column=1, padx=5, sticky="sw")
