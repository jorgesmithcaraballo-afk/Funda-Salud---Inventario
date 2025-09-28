import customtkinter as ctk
import threading
from tkinter import messagebox
from services.application.configuracion_service import ConfiguracionService
from resource.colors import (
    get_content_button_style,
    WHITE,
    CARD_BG,
    TABLE_ROW_ALT_BG,
    TEXT_MUTED,
    ERROR_TEXT_RED,
    DANGER_RED,
    DANGER_RED_HOVER,
)
from resource.sizes import BUTTON_HEIGHT, ENTRY_HEIGHT
from .modal_factory import create_modal
from resource.strings import (
    CATEGORIAS,
    GESTIONA_Y_ORGANIZA,
    NUEVA_CATEGORIA,
    AGREGAR,
    CERRAR,
    CARGANDO,
    RENOMBRAR,
    ELIMINAR,
)


def open_manage_categories_modal(view) -> None:
    """Modal de gestión de categorías."""
    if (
        hasattr(view, "_cats_win")
        and view._cats_win is not None
        and view._cats_win.winfo_exists()
    ):
        try:
            view._cats_win.focus_set()
        except Exception:
            pass
        return

    win, content = create_modal(view, CATEGORIAS)
    view._cats_win = win

    # Header
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", pady=(10, 10))
    header.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(
        header, text=CATEGORIAS, font=ctk.CTkFont(size=20, weight="bold")
    ).grid(row=0, column=0, sticky="n", pady=(0, 4))
    ctk.CTkLabel(
        header,
        text=GESTIONA_Y_ORGANIZA,
        font=ctk.CTkFont(size=14),
        text_color=TEXT_MUTED,
    ).grid(row=1, column=0, sticky="n")

    # Alta rápida
    add_frame = ctk.CTkFrame(content, fg_color=WHITE)
    add_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
    add_frame.grid_columnconfigure(1, weight=1)

    nuevaCategoria = ctk.CTkLabel(
        add_frame,
        text=NUEVA_CATEGORIA,
        font=ctk.CTkFont(
            size=18,
        ),
    )
    nuevaCategoria.grid(row=0, column=0, sticky="w")

    view._new_cat_var = ctk.StringVar()
    ctk.CTkEntry(add_frame, textvariable=view._new_cat_var, height=ENTRY_HEIGHT).grid(
        row=0, column=1, sticky="ew", padx=8
    )

    base = get_content_button_style()
    ctk.CTkButton(add_frame, text=AGREGAR, command=view._add_category, **base).grid(
        row=0, column=2, padx=(8, 0)
    )

    # Error label
    view._cat_error = ctk.CTkLabel(content, text="", text_color=ERROR_TEXT_RED)
    view._cat_error.grid(row=2, column=0, sticky="ew", pady=(0, 6))

    # Scroll
    view._cats_scroll = ctk.CTkScrollableFrame(content, fg_color=WHITE)
    view._cats_scroll.grid(row=3, column=0, sticky="nsew")
    content.grid_rowconfigure(3, weight=1)

    # Footer
    footer = ctk.CTkFrame(content, fg_color="transparent")
    footer.grid(row=4, column=0, sticky="we", pady=(12, 0))
    footer.grid_columnconfigure(0, weight=1)

    boton = ctk.CTkButton(footer, text=CERRAR, command=win.destroy, **base)
    boton.grid(row=0, column=0)

    _load_categories_list(view)


def _load_categories_list(view) -> None:
    for w in view._cats_scroll.winfo_children():
        w.destroy()
    # Use grid instead of pack to avoid mixing layout managers in the same parent
    loading = ctk.CTkLabel(view._cats_scroll, text=CARGANDO, anchor="w")
    loading.grid(row=0, column=0, sticky="ew", pady=6, padx=8)

    def _worker():
        try:
            rows = [
                {"nombre": n} for n in (ConfiguracionService.list_categories() or [])
            ]
        except Exception as e2:

            def _err():
                # Update error label only if widget still exists
                try:
                    if getattr(view, "_cats_scroll", None) and view._cats_scroll.winfo_exists():
                        view._cat_error.configure(text=f"Error cargando categorías: {e2}")
                except Exception:
                    pass

            try:
                view.after(0, _err)
            except Exception:
                pass
            rows = []

        if not rows:
            rows = [{"nombre": "General"}]

        def _render():
            # Do not render if window/scroll no longer exists
            try:
                if not getattr(view, "_cats_scroll", None) or not view._cats_scroll.winfo_exists():
                    return
            except Exception:
                return
            base = get_content_button_style()
            btn_inline = {
                k: v
                for k, v in base.items()
                if k not in ("width", "height", "fg_color", "hover_color")
            }

            # aseguramos que el scroll use todo el ancho
            view._cats_scroll.grid_columnconfigure(0, weight=1)

            for w in view._cats_scroll.winfo_children():
                w.destroy()

            for idx, r in enumerate(rows):
                nombre = r.get("nombre")
                rowf = ctk.CTkFrame(
                    view._cats_scroll,
                    fg_color=(WHITE if idx % 2 == 0 else CARD_BG),
                    corner_radius=4,
                )
                rowf.grid(row=idx, column=0, sticky="ew", pady=4, padx=4)

                # Configurar columnas internas
                rowf.grid_columnconfigure(0, weight=1)  # columna expandible para label
                rowf.grid_columnconfigure(1, weight=0)  # columna fija para acciones

                # Label alineado a la izquierda pero expandiendo en X
                label = ctk.CTkLabel(
                    rowf, text=nombre, anchor="w", font=ctk.CTkFont(size=18)
                )
                label.grid(row=0, column=0, sticky="ew", padx=6)

                # Botones alineados a la derecha
                actions = ctk.CTkFrame(rowf, fg_color="transparent")
                actions.grid(row=0, column=1, sticky="e", padx=6)

                ctk.CTkButton(
                    actions,
                    text=RENOMBRAR,
                    width=90,
                    height=30,
                    command=lambda n=nombre: view._rename_category_prompt(n),
                    **btn_inline,
                ).grid(row=0, column=0)

                ctk.CTkButton(
                    actions,
                    text=ELIMINAR,
                    width=90,
                    height=30,
                    fg_color=DANGER_RED,
                    hover_color=DANGER_RED_HOVER,
                    command=lambda n=nombre: view._delete_category(n),
                    **btn_inline,
                ).grid(row=0, column=1)

        try:
            view.after(0, _render)
        except Exception:
            # If the widget was destroyed before scheduling, just ignore
            pass

    # Use non-daemon thread to avoid Tkinter finalizers running after interpreter shutdown
    t = threading.Thread(target=_worker, daemon=False)
    t.start()
