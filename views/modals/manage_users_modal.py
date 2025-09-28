import customtkinter as ctk
import threading
from tkinter import messagebox
from services.application.configuracion_service import ConfiguracionService
from resource.colors import (
    get_content_button_style,
    WHITE,
    SURFACE_LIGHT,
    TABLE_ROW_ALT_BG,
    TEXT_DARK,
    TEXT_MUTED,
    SECONDARY_BLUE,
    SECONDARY_BLUE_HOVER,
    DANGER_RED,
    DANGER_RED_HOVER,
)
from resource.sizes import BUTTON_HEIGHT
from .modal_factory import create_modal
from .edit_user_modal import open_edit_user_modal
from .delete_user_modal import open_delete_user_modal
from resource.strings import (
    USUARIOS,
    USUARIOS_TITULO,
    LISTA_USUARIOS,
    ID,
    NOMBRE,
    APELLIDO,
    TIPO,
    ACCIONES,
    CERRAR,
    EDITAR,
    ELIMINAR,
)


def open_manage_users_modal(view) -> None:
    """Modal de gestión de usuarios con header fijo, cabecera de tabla, scrollable rows y footer."""
    win, content = create_modal(view, USUARIOS)
    view._manage_win = win

    # =========================================================
    # Row 0 → Header
    # =========================================================
    header = ctk.CTkFrame(content, fg_color=WHITE, height=60)
    header.grid(row=0, column=0, sticky="new", padx=16, pady=16)
    header.grid_propagate(False)
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        header,
        text=USUARIOS_TITULO,
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=TEXT_DARK,
    ).grid(row=0, column=0, sticky="n", pady=(8, 0))

    ctk.CTkLabel(
        header,
        text=LISTA_USUARIOS,
        font=ctk.CTkFont(size=14),
        text_color=TEXT_MUTED,
    ).grid(row=1, column=0, sticky="n")

    # =========================================================
    # Row 1 → Cabecera de tabla
    # =========================================================
    headers = [ID, NOMBRE, APELLIDO, TIPO, ACCIONES]
    header_container = ctk.CTkFrame(
        content, fg_color=SURFACE_LIGHT, height=40, corner_radius=4
    )
    header_container.grid(row=1, column=0, sticky="ew", padx=(16, 32), pady=16)
    header_container.grid_propagate(False)
    # Ensure content expands horizontally so header and rows share the same width
    content.grid_columnconfigure(0, weight=1)

    # 👇 distribuimos todas las columnas con el mismo peso
    for j in range(len(headers)):
        header_container.grid_columnconfigure(j, weight=1, uniform="col")
        # uniform="col" asegura que todas las columnas tengan el mismo ancho

    for j, text in enumerate(headers):
        ctk.CTkLabel(
            header_container,
            text=text,
            anchor="w",
            font=ctk.CTkFont(weight="bold"),
            text_color=TEXT_DARK,
            wraplength=120,  # 👈 permite que el texto se corte en varias líneas
        ).grid(row=0, column=j, sticky="nsew", padx=6, pady=6)

    # =========================================================
    # Row 2 → Scrollable tabla de usuarios
    # =========================================================
    view._users_scroll = ctk.CTkScrollableFrame(content, fg_color=WHITE)
    view._users_scroll.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
    content.grid_rowconfigure(2, weight=1)  # ocupa espacio dinámico
    # Ensure the scrollable content expands to the same width as the header
    view._users_scroll.grid_columnconfigure(0, weight=1)

    # =========================================================
    # Row 3 → Footer
    # =========================================================
    footer = ctk.CTkFrame(content, fg_color="transparent", height=50)
    footer.grid(row=3, column=0, sticky="sew", padx=16, pady=16)
    footer.grid_propagate(False)
    footer.grid_columnconfigure(0, weight=1)

    base = get_content_button_style()
    close = {**base, "fg_color": SECONDARY_BLUE, "hover_color": SECONDARY_BLUE_HOVER}
    ctk.CTkButton(footer, text=CERRAR, command=win.destroy, **close).grid(
        row=0, column=0, padx=10
    )

    # =========================================================
    # Cargar usuarios en tabla
    # =========================================================
    _load_users_list(view)


def _load_users_list(view) -> None:
    """Carga usuarios y pinta filas alternadas."""
    children = view._users_scroll.winfo_children()
    if children:
        for w in children:
            w.destroy()

    def _worker():
        try:
            rows = ConfiguracionService.list_users() or []
        except Exception as e:
            view._logger.error(f"Error cargando usuarios: {e}")
            rows = []

        def _render():
            base = get_content_button_style()
            btn_inline = {
                k: v
                for k, v in base.items()
                if k not in ("width", "height", "fg_color", "hover_color")
            }

            for i, row in enumerate(rows, start=1):
                bg = WHITE if i % 2 == 0 else TABLE_ROW_ALT_BG
                rframe = ctk.CTkFrame(view._users_scroll, fg_color=bg, corner_radius=4)
                rframe.grid(row=i, column=0, sticky="ew", padx=(12, 0), pady=0)

                # Use uniform column configuration to mirror header_container layout
                headers = [ID, NOMBRE, APELLIDO, TIPO, ACCIONES]
                for j in range(len(headers)):
                    rframe.grid_columnconfigure(j, weight=1, uniform="col")

                ctk.CTkLabel(rframe, text=str(row.get("id")), anchor="w").grid(
                    row=0, column=0, padx=6, pady=4, sticky="nsew"
                )
                ctk.CTkLabel(rframe, text=row.get("nombre") or "", anchor="w").grid(
                    row=0, column=1, padx=6, pady=4, sticky="nsew"
                )
                ctk.CTkLabel(rframe, text=row.get("apellido") or "", anchor="w").grid(
                    row=0, column=2, padx=6, pady=4, sticky="nsew"
                )
                ctk.CTkLabel(rframe, text=row.get("tipo") or "user", anchor="w").grid(
                    row=0, column=3, padx=6, pady=4, sticky="nsew"
                )

                actions = ctk.CTkFrame(rframe, fg_color="transparent")
                actions.grid(row=0, column=4, sticky="ew")
                actions.grid_columnconfigure((0, 1), weight=1)

                ctk.CTkButton(
                    actions,
                    text=EDITAR,
                    width=70,
                    fg_color=SECONDARY_BLUE,
                    hover_color=SECONDARY_BLUE_HOVER,
                    command=lambda r=row: open_edit_user_modal(view, r),
                    **btn_inline,
                ).grid(row=0, column=0)

                ctk.CTkButton(
                    actions,
                    text=ELIMINAR,
                    width=70,
                    fg_color=DANGER_RED,
                    hover_color=DANGER_RED_HOVER,
                    command=lambda r=row: open_delete_user_modal(view, r),
                    **btn_inline,
                ).grid(row=0, column=1)

        view.after(0, _render)

    threading.Thread(target=_worker, daemon=True).start()
