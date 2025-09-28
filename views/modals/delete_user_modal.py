import threading
from typing import Dict, Any

import customtkinter as ctk
from tkinter import messagebox

from services.application.configuracion_service import ConfiguracionService
from resource.colors import (
    get_content_button_style,
    CARD_BG,
    DANGER_RED,
)
from resource.sizes import ENTRY_HEIGHT
from .modal_factory import create_modal
from resource.strings import (
    PROTEGIDO,
    NO_ELIMINAR_ADMIN_PRINCIPAL,
    CONFIRMAR_ELIMINACION_DE_USUARIO,
    ESTA_ACCION_NO_PUEDE_SER_REVERTIDA,
    USUARIO,
    USUARIO_ELIMINADO,
    NO_SE_PUDO_ELIMINAR_USUARIO,
    ELIMINAR,
    CANCELAR,
)


def open_delete_user_modal(view, row: Dict[str, Any]) -> None:
    """Open a confirmation modal to delete a user and refresh the users list on success."""
    uid = row.get("id")
    nombre = (row.get("nombre") or "").strip()
    tipo = (row.get("tipo") or "user").strip().lower()

    if tipo == "admin" and nombre.lower() == "naila":
        messagebox.showwarning(PROTEGIDO, NO_ELIMINAR_ADMIN_PRINCIPAL)
        return

    win, container = create_modal(view, f"{ELIMINAR} {USUARIO} #{uid}")
    # Center layout: use three-column grid where column 1 holds content
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=0)
    container.grid_columnconfigure(2, weight=1)

    title = ctk.CTkLabel(
        container,
        text=CONFIRMAR_ELIMINACION_DE_USUARIO,
        font=ctk.CTkFont(size=18, weight="bold"),
    )
    title.grid(row=0, column=1, sticky="n", pady=(0, 8))

    # Contenedor con fondo y bordes redondeados
    card = ctk.CTkFrame(
        container,
        fg_color=CARD_BG,  # background for card container
        corner_radius=12,  # rounded corners
    )
    card.grid(row=1, column=1, padx=20, pady=10, sticky="n")

    # Texto dentro del contenedor
    label = ctk.CTkLabel(
        card,
        text=f"ID: {uid}\nNombre: {nombre}\nTipo: {tipo}",
        font=ctk.CTkFont(size=20),
        anchor="w",
        justify="left",
    )
    label.pack(
        padx=12, pady=12, anchor="w"
    )  # padding interno y alineación a la izquierda

    messageFooter = ctk.CTkLabel(
        container, text=ESTA_ACCION_NO_PUEDE_SER_REVERTIDA, text_color=DANGER_RED
    )
    messageFooter.grid(row=2, column=1, sticky="n", pady=(8, 4))

    def do_delete() -> None:
        def worker() -> None:
            try:
                ok = ConfiguracionService.delete_user(uid, nombre, tipo)
                if ok:
                    view.after(
                        0, lambda: messagebox.showinfo(USUARIO, USUARIO_ELIMINADO)
                    )
                    view.after(0, win.destroy)
                    view.after(0, view._load_users_list)
                else:
                    view.after(
                        0,
                        lambda: messagebox.showwarning(
                            PROTEGIDO,
                            NO_SE_PUDO_ELIMINAR_USUARIO,
                        ),
                    )
            except Exception as e:
                view._logger.error(f"Error eliminando usuario: {e}")
                view.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"No se pudo eliminar usuario:\n{e}"
                    ),
                )

        threading.Thread(target=worker, daemon=True).start()

    base = get_content_button_style()

    btns = ctk.CTkFrame(container, fg_color="transparent")
    btns.grid(row=4, column=1, sticky="n", pady=12)

    # Agrupar botones uno al lado del otro conservando estilos
    buttons_frame = ctk.CTkFrame(btns, fg_color="transparent")
    buttons_frame.grid(row=0, column=0)

    botonCancelar = ctk.CTkButton(
        buttons_frame, text=CANCELAR, command=win.destroy, **base
    )
    botonCancelar.grid(row=0, column=0, padx=(0, 10))

    botonEliminar = ctk.CTkButton(
        buttons_frame,
        text=ELIMINAR,
        command=do_delete,
        **base,
    )
    botonEliminar.grid(row=0, column=1, padx=(10, 0))
