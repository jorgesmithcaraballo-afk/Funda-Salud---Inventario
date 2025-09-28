import customtkinter as ctk
import threading
from tkinter import messagebox
from services.application.configuracion_service import ConfiguracionService
from resource.colors import (
    get_content_button_style,
    WHITE,
    TEXT_DARK,
    TEXT_MUTED,
    GRAY,
    DARK_GRAY,
    SECONDARY_BLUE,
    SECONDARY_BLUE_HOVER,
)
from resource.sizes import CONTENT_SELECT_WIDTH, CONTENT_SELECT_HEIGHT
from .modal_factory import create_modal
from .delete_product_confirmation_modal import open_delete_product_confirmation_modal


def open_delete_product_modal(view) -> None:
    """Paso 1: selección de producto a eliminar."""
    if hasattr(view, "_del_prod_win") and view._del_prod_win.winfo_exists():
        view._del_prod_win.focus_set()
        return

    win, content = create_modal(view, "Eliminar Producto (Paso 1 de 2)")
    view._del_prod_win = win
    view._del_prod_open = True
    view._del_load_token = getattr(view, "_del_load_token", 0) + 1

    # Header
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", pady=(10, 12))
    header.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(
        header,
        text="Seleccione el producto a eliminar",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=TEXT_DARK,
    ).grid(row=0, column=0, sticky="n", pady=(0, 4))
    ctk.CTkLabel(
        header,
        text="Busque por descripción o por código",
        font=ctk.CTkFont(size=14),
        text_color=TEXT_MUTED,
    ).grid(row=1, column=0, sticky="n")

    # Form
    form = ctk.CTkFrame(content, fg_color=WHITE)
    form.grid(row=1, column=0, sticky="nsew")
    form.grid_columnconfigure(1, weight=1)

    view._del_desc_var = ctk.StringVar()
    view._del_code_var = ctk.StringVar()

    ctk.CTkLabel(form, text="Descripción").grid(
        row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 6)
    )
    view._del_desc_cb = ctk.CTkComboBox(
        form,
        variable=view._del_desc_var,
        values=[],
        width=CONTENT_SELECT_WIDTH,
        height=CONTENT_SELECT_HEIGHT,
        command=lambda _=None: view._on_delete_desc_selected(),
    )
    view._del_desc_cb.grid(row=0, column=1, sticky="ew", pady=(0, 10))

    ctk.CTkLabel(form, text="Código").grid(
        row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 6)
    )
    view._del_code_cb = ctk.CTkComboBox(
        form,
        variable=view._del_code_var,
        values=[],
        width=CONTENT_SELECT_WIDTH,
        height=CONTENT_SELECT_HEIGHT,
        command=lambda _=None: view._on_delete_code_selected(),
    )
    view._del_code_cb.grid(row=1, column=1, sticky="ew")

    # Footer
    footer = ctk.CTkFrame(content, fg_color="transparent")
    footer.grid(row=2, column=0, sticky="e", pady=(16, 0))
    base = get_content_button_style()
    cancel = {**base, "fg_color": GRAY, "hover_color": DARK_GRAY}
    primary = {**base, "fg_color": SECONDARY_BLUE, "hover_color": SECONDARY_BLUE_HOVER}

    ctk.CTkButton(footer, text="Cancelar", command=win.destroy, **cancel).grid(
        row=0, column=1, padx=(8, 0)
    )
    view._del_next_btn = ctk.CTkButton(
        footer,
        text="Siguiente: Verificar Datos",
        command=lambda: open_delete_product_confirmation_modal(view),
        state="disabled",
        **primary
    )
    view._del_next_btn.grid(row=0, column=0)

    threading.Thread(target=view._load_product_data_for_delete, daemon=True).start()
