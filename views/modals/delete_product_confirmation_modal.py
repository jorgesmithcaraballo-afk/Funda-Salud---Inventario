import threading
from typing import Any, Dict, Optional

import customtkinter as ctk
from tkinter import messagebox

from services.application.configuracion_service import ConfiguracionService
from resource.colors import (
    get_content_button_style,
    WHITE,
    DANGER_RED,
    DANGER_RED_HOVER,
    NEUTRAL_BORDER,
    GRAY,
    DARK_GRAY,
    TEXT_MUTED,
)
from .modal_factory import create_modal


def open_delete_product_confirmation_modal(view) -> None:
    """Open final confirmation modal displaying product summary and history."""
    if not getattr(view, "_selected_product_to_delete", None):
        messagebox.showwarning(
            "Selección Requerida",
            "Por favor, seleccione un producto válido antes de continuar.",
        )
        return

    if (
        hasattr(view, "_del_confirm_win")
        and getattr(view, "_del_confirm_win").winfo_exists()
    ):
        view._del_confirm_win.focus_set()
        return

    win, container = create_modal(
        view, "Eliminar Producto: Confirmación Final (Paso 2 de 2)"
    )
    view._del_confirm_win = win
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(1, weight=1)

    # Header
    header = ctk.CTkFrame(container, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
    header.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(
        header,
        text="Resumen del Producto a Eliminar",
        font=ctk.CTkFont(size=18, weight="bold"),
    ).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(
        header,
        text="Esta acción es irreversible. Se eliminará el producto y todo su historial.",
        text_color=DANGER_RED,
        font=ctk.CTkFont(size=14, weight="bold"),
    ).grid(row=1, column=0, sticky="w")

    # History area
    view._history_scroll_frame = ctk.CTkScrollableFrame(
        container, label_text="Historial de Movimientos", fg_color=WHITE
    )
    view._history_scroll_frame.grid(row=1, column=0, sticky="nsew")
    view._history_scroll_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(view._history_scroll_frame, text="Cargando historial...").pack()

    # Buttons
    btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    btn_frame.grid(row=2, column=0, sticky="e", pady=(20, 0))

    base = get_content_button_style()
    cancel = {
        **base,
        "fg_color": GRAY,
        "hover_color": DARK_GRAY,
        "text_color": "white",
        "font": ctk.CTkFont(size=16),
    }
    danger = {
        **base,
        "fg_color": DANGER_RED,
        "hover_color": DANGER_RED_HOVER,
        "text_color": "white",
        "font": ctk.CTkFont(size=16, weight="bold"),
    }

    ctk.CTkButton(btn_frame, text="Cancelar", command=win.destroy, **cancel).grid(
        row=0, column=1, padx=(10, 0)
    )
    view._del_confirm_btn = ctk.CTkButton(
        btn_frame,
        text="Confirmar Eliminación Definitiva",
        command=lambda: _execute_delete_product(view),
        state="disabled",
        **danger,
    )
    view._del_confirm_btn.grid(row=0, column=0)

    # Load and render history
    threading.Thread(
        target=lambda: _load_and_display_history(view), daemon=True
    ).start()


def _load_and_display_history(view) -> None:
    product_id = view._selected_product_to_delete.get("id")
    if product_id is None:
        view.after(
            0, lambda: messagebox.showerror("Error", "ID de producto no encontrado.")
        )
        return
    try:
        history = ConfiguracionService.get_product_history(product_id)
        view.after(0, lambda: _render_history(view, history))
    except Exception as e:
        view._logger.error(f"Error fetching product history: {e}")
        view.after(
            0,
            lambda: messagebox.showerror(
                "Error", f"No se pudo cargar el historial: {e}"
            ),
        )


def _render_history(view, history: Dict[str, Any]) -> None:
    # Clear placeholder
    for widget in view._history_scroll_frame.winfo_children():
        widget.destroy()

    def _fmt_int_es(value: Any) -> str:
        try:
            n = int(float(value))
            return f"{n:,}".replace(",", ".")
        except Exception:
            return "N/A"

    def _fmt_dec_es(value: Any) -> str:
        try:
            x = float(value)
            s = f"{x:,.2f}"
            return s.replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return "N/A"

    def render_kv(label: str, value: Any) -> None:
        safe_val = "N/A" if value is None or value == "" else value
        ctk.CTkLabel(view._history_scroll_frame, text=f"{label}: {safe_val}").pack(
            anchor="w", padx=10
        )

    def render_int(label: str, value: Any) -> None:
        ctk.CTkLabel(
            view._history_scroll_frame, text=f"{label}: {_fmt_int_es(value)}"
        ).pack(anchor="w", padx=10)

    def render_money(label: str, value: Any) -> None:
        ctk.CTkLabel(
            view._history_scroll_frame, text=f"{label}: {_fmt_dec_es(value)}"
        ).pack(anchor="w", padx=10)

    def add_inventory_section(inv: Optional[Dict[str, Any]]):
        ctk.CTkLabel(
            view._history_scroll_frame,
            text="Datos Principales",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 2))
        if not inv:
            ctk.CTkLabel(
                view._history_scroll_frame,
                text="No hay registro.",
                text_color=TEXT_MUTED,
            ).pack(anchor="w", padx=10)
        else:
            render_kv("Descripcion Insumo", inv.get("descripcion_insumo"))
            render_kv("Categoría", inv.get("categoria"))
            render_money("Costo Unitario", inv.get("costo_unitario"))
            render_kv("Código", inv.get("codigo"))
            render_kv("ID", inv.get("id"))
        ctk.CTkFrame(
            view._history_scroll_frame, height=1, fg_color=NEUTRAL_BORDER
        ).pack(fill="x", pady=10, padx=10)

    def add_movement_section(title: str, mov: Optional[Dict[str, Any]]):
        ctk.CTkLabel(
            view._history_scroll_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 2))
        if not mov:
            ctk.CTkLabel(
                view._history_scroll_frame,
                text="No hay registro.",
                text_color=TEXT_MUTED,
            ).pack(anchor="w", padx=10)
        else:
            cant = mov.get("cantidad")
            costo = mov.get("costo")
            render_int("Cantidad", cant)
            render_money("Costo", costo)
            try:
                if cant is not None and costo is not None:
                    monto = float(cant) * float(costo)
                    render_money("Monto", monto)
            except Exception:
                pass
        ctk.CTkFrame(
            view._history_scroll_frame, height=1, fg_color=NEUTRAL_BORDER
        ).pack(fill="x", pady=10, padx=10)

    inv = history.get("inventario") or {}
    ei = history.get("existencia_inicial") or {}
    en = history.get("entradas") or {}
    sa = history.get("salidas") or {}
    ef = history.get("existencia_final")

    add_inventory_section(inv)
    add_movement_section("Existencia Inicial", ei if ei else None)
    add_movement_section("Entradas", en if en else None)
    add_movement_section("Salidas", sa if sa else None)

    if not ef:
        try:
            ei_cant = float(ei.get("cantidad") or 0)
        except Exception:
            ei_cant = 0.0
        try:
            e_cant = float(en.get("cantidad") or 0)
        except Exception:
            e_cant = 0.0
        try:
            s_cant = float(sa.get("cantidad") or 0)
        except Exception:
            s_cant = 0.0

        final_cant = ei_cant + e_cant - s_cant
        try:
            final_costo = float(inv.get("costo_unitario") or 0)
        except Exception:
            final_costo = 0.0

        ef_calc = {"cantidad": final_cant, "costo": final_costo}
        add_movement_section("Existencia Final", ef_calc)
    else:
        add_movement_section("Existencia Final", ef)

    view._del_confirm_btn.configure(state="normal")


def _execute_delete_product(view) -> None:
    product_id = view._selected_product_to_delete.get("id")
    if product_id is None:
        messagebox.showerror("Error", "ID de producto no válido.")
        return
    if not messagebox.askyesno(
        "Confirmación Final",
        "¿Está absolutamente seguro? Esta acción no se puede deshacer.",
    ):
        return

    view._del_confirm_btn.configure(state="disabled", text="Eliminando...")

    def worker() -> None:
        try:
            success = ConfiguracionService.delete_product_full(product_id)
            if success:
                view.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Éxito", "Producto y su historial eliminados correctamente."
                    ),
                )
                view.after(0, view._del_confirm_win.destroy)
                view.after(0, view._del_prod_win.destroy)
                view.after(
                    0,
                    lambda: threading.Thread(
                        target=view._load_product_data_for_delete, daemon=True
                    ).start(),
                )
            else:
                view.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error",
                        "No se pudo eliminar el producto. Revise los registros.",
                    ),
                )
                view.after(
                    0,
                    lambda: view._del_confirm_btn.configure(
                        state="normal", text="Confirmar Eliminación Definitiva"
                    ),
                )
        except Exception as e:
            view._logger.error(f"Exception during product deletion: {e}")
            view.after(
                0,
                lambda: messagebox.showerror(
                    "Error Crítico", f"Ocurrió un error inesperado: {e}"
                ),
            )
            view.after(
                0,
                lambda: view._del_confirm_btn.configure(
                    state="normal", text="Confirmar Eliminación Definitiva"
                ),
            )

    threading.Thread(target=worker, daemon=True).start()
