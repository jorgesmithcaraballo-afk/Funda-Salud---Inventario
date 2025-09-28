"""
System configuration view for managing users, categories, and product deletion.
"""

# ---------------------------
# Standard library imports
# ---------------------------
import hashlib
import logging
import os as _os
import threading
from tkinter import messagebox
from typing import Any, Dict, Optional

# ---------------------------
# External library imports
# ---------------------------
import customtkinter as ctk

# ---------------------------
# Internal project imports
# ---------------------------
from services.application.configuracion_service import ConfiguracionService
from resource.colors import (
    TEXT_PRIMARY,
    WHITE,
    TABLE_ROW_ALT_BG,
    NEUTRAL_BORDER,
    DANGER_RED,
    DANGER_RED_HOVER,
    SECONDARY_BLUE,
    SECONDARY_BLUE_HOVER,
    ERROR_TEXT_RED,
    get_content_button_style,
)
from resource.sizes import (
    BUTTON_HEIGHT,
    ENTRY_HEIGHT,
    CONTENT_SELECT_WIDTH,
    CONTENT_SELECT_HEIGHT,
)
from resource.strings import (
    CONFIGURACION_TITLE,
    CONFIGURACION_DEL_SISTEMA,
    USUARIOS,
    AGREGAR_USUARIO,
    CATEGORIAS,
    ELIMINAR_PRODUCTOS,
)
from views.modals.add_user_modal import open_add_user_modal
from views.modals.manage_users_modal import open_manage_users_modal
from views.modals.manage_categories_modal import open_manage_categories_modal
from views.modals.delete_product_modal import open_delete_product_modal
from views.modals.modal_factory import create_modal
from views.toolbar import Toolbar


class ConfiguracionView(ctk.CTkFrame):
    """Vista principal de configuración (usuarios, categorías y eliminación de productos)."""

    # ---------------------------
    # Init / Layout raíz
    # ---------------------------
    def __init__(self, master: Any, controlador: Any):
        super().__init__(master)
        self.controlador = controlador
        self._logger = logging.getLogger(__name__)
        self.previous_view = "filtro"  # Vista anterior por defecto

        self.configure(fg_color=WHITE)
        # Root grid: row 0 toolbar, row 1 content (expand)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_content()

    # ---------------------------
    # Header principal
    # ---------------------------
    def _build_header(self) -> None:
        toolbar = Toolbar(
            self,
            title=f"{CONFIGURACION_TITLE}",
            on_go_subir=self.go_back,
            on_go_chat=None,
            on_go_config=None,
        )
        toolbar.grid(row=0, column=0, sticky="ew")
        # Only show back (subir) button in this toolbar
        try:
            toolbar.configure_buttons(show_chat=False, show_config=False)
        except Exception:
            pass

    # ---------------------------
    # Contenido principal
    # ---------------------------
    def _build_content(self) -> None:
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=32)
        content_frame.grid_columnconfigure(0, weight=1)

        actions_bar = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_bar.grid(row=1, column=0, sticky="n")
        actions_bar.grid_columnconfigure(0, weight=1)

        btn_style = get_content_button_style()

        ctk.CTkButton(
            actions_bar,
            text=USUARIOS,
            command=lambda: open_manage_users_modal(self),
            **btn_style,
        ).grid(row=0, column=0, pady=8, sticky="ew")

        ctk.CTkButton(
            actions_bar,
            text=AGREGAR_USUARIO,
            command=lambda: open_add_user_modal(self),
            **btn_style,
        ).grid(row=1, column=0, pady=8, sticky="ew")

        ctk.CTkButton(
            actions_bar,
            text=CATEGORIAS,
            command=lambda: open_manage_categories_modal(self),
            **btn_style,
        ).grid(row=2, column=0, pady=8, sticky="ew")

        ctk.CTkFrame(actions_bar, height=2, fg_color=NEUTRAL_BORDER).grid(
            row=3, column=0, sticky="ew", pady=20
        )

        delete_btn_style = {
            **btn_style,
            "fg_color": DANGER_RED,
            "hover_color": DANGER_RED_HOVER,
        }
        ctk.CTkButton(
            actions_bar,
            text=ELIMINAR_PRODUCTOS,
            command=lambda: open_delete_product_modal(self),
            **delete_btn_style,
        ).grid(row=4, column=0, pady=8, sticky="ew")

    # (Modal factory wrappers removed; calling modal functions directly)

    # ---------------------------
    # Navegación
    # ---------------------------
    def go_back(self) -> None:
        try:
            target = getattr(self, "previous_view", "filtro") or "filtro"
            if hasattr(self.controlador, "mostrar_vista"):
                self.controlador.mostrar_vista(target)
        except Exception as e:
            self._logger.error(f"Error in go_back: {e}")
            try:
                messagebox.showerror("Error", "No se pudo volver a la vista anterior.")
            except Exception:
                pass

    # ======================================================================
    # Eliminación de producto (helpers compartidos con modales)
    # ======================================================================

    def _load_product_data_for_delete(self) -> None:
        """Carga de catálogos para el modal de eliminación."""
        try:
            codes, descs, code_map, desc_label_to_code, code_to_desc_label = (
                ConfiguracionService.load_inventario_codes_map()
            )
            current_token = getattr(self, "_del_load_token", 0)

            def _update_ui():
                if not getattr(self, "_del_prod_open", False):
                    return
                try:
                    if not (
                        hasattr(self, "_del_prod_win")
                        and self._del_prod_win.winfo_exists()
                    ):
                        return
                except Exception:
                    return
                if current_token != getattr(self, "_del_load_token", 0):
                    return

                self._del_all_codes = codes
                self._del_all_descs = descs
                self._del_code_map = code_map
                self._del_desc_map_lower = {
                    k.lower(): v for k, v in desc_label_to_code.items()
                }
                self._del_code_to_desc_map = code_to_desc_label

                try:
                    if getattr(self, "_del_desc_cb", None):
                        self._del_desc_cb.configure(values=self._del_all_descs)
                    if getattr(self, "_del_code_cb", None):
                        self._del_code_cb.configure(values=self._del_all_codes)
                    if getattr(self, "_del_desc_var", None) is not None:
                        self._del_desc_var.set("")
                    if getattr(self, "_del_code_var", None) is not None:
                        self._del_code_var.set("")
                except Exception:
                    pass

            if getattr(self, "_del_prod_open", False):
                self.after(0, _update_ui)

        except Exception as e:
            self._logger.error(f"Error loading product data for deletion: {e}")
            self.after(
                0,
                lambda: messagebox.showerror(
                    "Error", "No se pudieron cargar los productos."
                ),
            )

    def _on_delete_desc_selected(self, _=None) -> None:
        desc = self._del_desc_var.get()
        if not desc or not hasattr(self, "_del_desc_map_lower"):
            return
        code = self._del_desc_map_lower.get(desc.lower())
        if code:
            product_data = self._del_code_map.get(code)
            if product_data:
                self._selected_product_to_delete = product_data
                self._del_code_var.set(code)
                self._del_next_btn.configure(state="normal")
                return
        self._selected_product_to_delete = None
        self._del_next_btn.configure(state="disabled")

    def _on_delete_code_selected(self, _=None) -> None:
        code = self._del_code_var.get()
        if not code or not hasattr(self, "_del_code_map"):
            return
        product_data = self._del_code_map.get(code)
        if product_data:
            self._selected_product_to_delete = product_data
            self._del_desc_var.set(self._del_code_to_desc_map.get(code, ""))
            self._del_next_btn.configure(state="normal")
            return
        self._selected_product_to_delete = None
        self._del_next_btn.configure(state="disabled")

    # History UI y confirmación movidos a views/modals/delete_product_confirmation_modal.py

    # _execute_delete_product moved to modal

    # ======================================================================
    # Usuarios: crear / validar / guardar
    # ======================================================================

    def _validate_user_form(self) -> bool:
        nombre = (self._nombre_var.get() or "").strip()
        apellido = (self._apellido_var.get() or "").strip()
        contrasena = (self._contrasena_var.get() or "").strip()
        contrasena2 = (self._contrasena2_var.get() or "").strip()
        tipo = (self._tipo_var.get() or "").strip().lower()

        if not nombre or not apellido or not contrasena:
            self._error_label.configure(
                text="Nombre, Apellido y Contraseña son obligatorios"
            )
            return False
        if tipo not in ("admin", "user"):
            self._error_label.configure(text="Tipo inválido. Usa admin o user")
            return False
        if not (5 <= len(contrasena) <= 8):
            self._error_label.configure(
                text="La contraseña debe tener entre 5 y 8 caracteres"
            )
            return False
        if contrasena != contrasena2:
            self._error_label.configure(text="Las contraseñas no coinciden")
            return False
        self._error_label.configure(text="")
        return True

    def _save_new_user(self) -> None:
        if not self._validate_user_form():
            return
        nombre = self._nombre_var.get().strip()
        apellido = self._apellido_var.get().strip()
        contrasena = self._contrasena_var.get().strip()
        tipo = self._tipo_var.get().strip().lower()

        try:
            self._save_btn.configure(state="disabled")
        except Exception:
            pass

        try:
            ok = ConfiguracionService.add_user(
                nombre=nombre, apellido=apellido, contrasena=contrasena, tipo=tipo
            )
            if ok:
                messagebox.showinfo("Usuario", "Usuario creado correctamente")
                if hasattr(self, "_add_user_win") and self._add_user_win is not None:
                    self._add_user_win.destroy()
                    self._add_user_win = None
            else:
                messagebox.showwarning(
                    "Usuario", "No se pudo crear el usuario. Intenta nuevamente"
                )
        except Exception as e:
            self._logger.error(f"Error creando usuario: {e}")
            messagebox.showerror("Error", f"No se pudo crear el usuario:\n{e}")
        finally:
            try:
                self._save_btn.configure(state="normal")
            except Exception:
                pass

    # ======================================================================
    # Usuarios: listar / editar / eliminar
    # ======================================================================

    def _load_users_list(self) -> None:
        """Carga usuarios (thread) y pinta filas alternadas."""
        # Limpia dejando la cabecera intacta si existe
        children = self._users_scroll.winfo_children()
        if children:
            for w in children[1:]:
                w.destroy()

        def _worker():
            try:
                rows = ConfiguracionService.list_users() or []
            except Exception as e:
                self._logger.error(f"Error cargando usuarios: {e}")
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
                    rframe = ctk.CTkFrame(
                        self._users_scroll, fg_color=bg, corner_radius=4
                    )
                    rframe.grid(row=i, column=0, sticky="ew", padx=2, pady=2)
                    rframe.grid_columnconfigure(5, weight=1)

                    ctk.CTkLabel(
                        rframe, text=str(row.get("id")), width=60, anchor="w"
                    ).grid(row=0, column=0, padx=6, pady=4)
                    ctk.CTkLabel(
                        rframe, text=row.get("nombre") or "", width=150, anchor="w"
                    ).grid(row=0, column=1, padx=6, pady=4)
                    ctk.CTkLabel(
                        rframe, text=row.get("apellido") or "", width=150, anchor="w"
                    ).grid(row=0, column=2, padx=6, pady=4)
                    ctk.CTkLabel(
                        rframe, text=str(row.get("tiempo") or ""), width=80, anchor="w"
                    ).grid(row=0, column=3, padx=6, pady=4)
                    ctk.CTkLabel(
                        rframe, text=row.get("tipo") or "user", width=100, anchor="w"
                    ).grid(row=0, column=4, padx=6, pady=4)

                    actions = ctk.CTkFrame(rframe, fg_color="transparent")
                    actions.grid(row=0, column=5, sticky="e", padx=6)

                    ctk.CTkButton(
                        actions,
                        text="Editar",
                        width=70,
                        fg_color=SECONDARY_BLUE,
                        hover_color=SECONDARY_BLUE_HOVER,
                        command=lambda r=row: self._open_edit_user_modal(r),
                        **btn_inline,
                    ).grid(row=0, column=0, padx=(0, 6))

                    ctk.CTkButton(
                        actions,
                        text="Eliminar",
                        width=70,
                        fg_color=DANGER_RED,
                        hover_color=DANGER_RED_HOVER,
                        command=lambda r=row: self._delete_user(r),
                        **btn_inline,
                    ).grid(row=0, column=1)

            self.after(0, _render)

        threading.Thread(target=_worker, daemon=True).start()

    def _open_edit_user_modal(self, row: dict) -> None:
        """Editar usuario (con bloqueo de tipo si es 'naila')."""
        win, container = create_modal(self, f"Editar usuario #{row.get('id')}")
        container.grid_columnconfigure(0, weight=1)

        nombre_var = ctk.StringVar(value=row.get("nombre") or "")
        apellido_var = ctk.StringVar(value=row.get("apellido") or "")
        contrasena_var = ctk.StringVar(value="")
        tipo_var = ctk.StringVar(value=row.get("tipo") or "user")

        def add_field(parent, row_idx: int, label_text: str, widget: ctk.CTkBaseClass):
            ctk.CTkLabel(parent, text=label_text, anchor="w").grid(
                row=row_idx, column=0, sticky="ew", pady=(0, 4)
            )
            widget.grid(row=row_idx + 1, column=0, sticky="ew", pady=(0, 12))

        add_field(
            container,
            0,
            "Nombre",
            ctk.CTkEntry(container, textvariable=nombre_var, height=ENTRY_HEIGHT),
        )
        add_field(
            container,
            2,
            "Apellido",
            ctk.CTkEntry(container, textvariable=apellido_var, height=ENTRY_HEIGHT),
        )
        add_field(
            container,
            4,
            "Nueva contraseña",
            ctk.CTkEntry(
                container, textvariable=contrasena_var, show="*", height=ENTRY_HEIGHT
            ),
        )

        is_naila = (row.get("nombre") or "").strip().lower() == "naila"
        if is_naila:
            add_field(
                container,
                6,
                "Tipo",
                ctk.CTkLabel(container, text=row.get("tipo") or "user"),
            )
        else:
            add_field(
                container,
                6,
                "Tipo",
                ctk.CTkOptionMenu(
                    container,
                    variable=tipo_var,
                    values=["admin", "user"],
                    width=CONTENT_SELECT_WIDTH,
                    height=CONTENT_SELECT_HEIGHT,
                ),
            )

        error_label = ctk.CTkLabel(container, text="", text_color=ERROR_TEXT_RED)
        error_label.grid(row=8, column=0, sticky="ew", pady=(8, 0))

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
            if (contrasena_var.get() or "") and not (
                5 <= len(contrasena_var.get()) <= 8
            ):
                error_label.configure(
                    text="La nueva contraseña debe tener entre 5 y 8 caracteres"
                )
                return False
            error_label.configure(text="")
            return True

        def save_changes() -> None:
            if not validate():
                return
            nombre = nombre_var.get().strip()
            apellido = apellido_var.get().strip()
            npass = (contrasena_var.get() or "").strip()
            tipo = (
                (row.get("tipo") or "user") if is_naila else (tipo_var.get() or "user")
            )
            tipo = (tipo or "user").strip().lower()

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
                messagebox.showinfo("Usuario", "Cambios guardados")
                win.destroy()
                self._load_users_list()
            except Exception as e:
                self._logger.error(f"Error guardando cambios: {e}")
                messagebox.showerror("Error", f"No se pudo guardar cambios:\n{e}")

        btns = ctk.CTkFrame(container, fg_color="transparent")
        btns.grid(row=9, column=0, sticky="e", pady=12)
        base = get_content_button_style()
        ctk.CTkButton(btns, text="Cancelar", command=win.destroy, **base).grid(
            row=0, column=1, padx=(8, 0)
        )
        ctk.CTkButton(btns, text="Guardar", command=save_changes, **base).grid(
            row=0, column=0
        )

    def _delete_user(self, row: dict) -> None:
        self._open_delete_user_modal(row)

    def _open_delete_user_modal(self, row: dict) -> None:
        uid = row.get("id")
        nombre = (row.get("nombre") or "").strip()
        tipo = (row.get("tipo") or "user").strip().lower()
        if tipo == "admin" and nombre.lower() == "naila":
            messagebox.showwarning(
                "Protegido", "No se puede eliminar el admin principal (naila)"
            )
            return

        win, container = create_modal(self, f"Eliminar usuario #{uid}")
        container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            container,
            text="Confirmar eliminación de usuario",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))
        ctk.CTkLabel(container, text=f"ID: {uid}\nNombre: {nombre}\nTipo: {tipo}").grid(
            row=1, column=0, sticky="w"
        )
        ctk.CTkLabel(
            container, text="Esta acción no se puede deshacer.", text_color=DANGER_RED
        ).grid(row=2, column=0, sticky="w", pady=(8, 12))

        btns = ctk.CTkFrame(container, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="e")
        base = get_content_button_style()

        def do_delete():
            try:
                ok = ConfiguracionService.delete_user(uid, nombre, tipo)
                if ok:
                    messagebox.showinfo("Usuario", "Usuario eliminado")
                    win.destroy()
                    self._load_users_list()
                else:
                    messagebox.showwarning(
                        "Protegido",
                        "No se pudo eliminar el usuario (protegido o error)",
                    )
            except Exception as e:
                self._logger.error(f"Error eliminando usuario: {e}")
                messagebox.showerror("Error", f"No se pudo eliminar usuario:\n{e}")

        ctk.CTkButton(btns, text="Cancelar", command=win.destroy, **base).grid(
            row=0, column=1, padx=(8, 0)
        )
        ctk.CTkButton(btns, text="Eliminar", command=do_delete, **base).grid(
            row=0, column=0
        )

    # ======================================================================
    # Categorías
    # ======================================================================

    def _refresh_other_views(self) -> None:
        try:
            subir = getattr(self.controlador, "frames", {}).get("subir")
            if subir and hasattr(subir, "reset_view_state"):
                subir.reset_view_state()
        except Exception:
            pass
        try:
            filtro = getattr(self.controlador, "frames", {}).get("filtro")
            if filtro and hasattr(filtro, "reset_view_state"):
                filtro.reset_view_state()
        except Exception:
            pass

    def _load_categories_list(self) -> None:
        if not hasattr(self, "_cats_scroll"):
            return
        for w in self._cats_scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(self._cats_scroll, text="Cargando categorías...", anchor="w").pack(
            fill="x", pady=6, padx=8
        )

        def _worker():
            try:
                rows = [
                    {"nombre": n}
                    for n in (ConfiguracionService.list_categories() or [])
                ]
            except Exception as e2:

                def _err():
                    self._cat_error.configure(text=f"Error cargando categorías: {e2}")

                self.after(0, _err)
                rows = []

            if not rows:
                rows = [{"nombre": "General"}]

            def _render():
                base = get_content_button_style()
                btn_inline = {
                    k: v
                    for k, v in base.items()
                    if k not in ("width", "height", "fg_color", "hover_color")
                }
                for w in self._cats_scroll.winfo_children():
                    w.destroy()
                for idx, r in enumerate(rows):
                    nombre = (
                        r.get("nombre") if isinstance(r, dict) else (r[0] if r else "")
                    )
                    rowf = ctk.CTkFrame(
                        self._cats_scroll,
                        fg_color=(WHITE if idx % 2 == 0 else TABLE_ROW_ALT_BG),
                        corner_radius=4,
                    )
                    rowf.grid(row=idx, column=0, sticky="ew", pady=4, padx=4)
                    rowf.grid_columnconfigure(1, weight=1)
                    ctk.CTkLabel(rowf, text=nombre, anchor="w").grid(
                        row=0, column=0, sticky="w", padx=6
                    )

                    actions = ctk.CTkFrame(rowf, fg_color="transparent")
                    actions.grid(row=0, column=1, sticky="e")
                    ctk.CTkButton(
                        actions,
                        text="Renombrar",
                        width=90,
                        height=BUTTON_HEIGHT,
                        command=lambda n=nombre: self._rename_category_prompt(n),
                        **btn_inline,
                    ).grid(row=0, column=0, padx=(0, 6))
                    ctk.CTkButton(
                        actions,
                        text="Eliminar",
                        width=80,
                        height=BUTTON_HEIGHT,
                        fg_color=DANGER_RED,
                        hover_color=DANGER_RED_HOVER,
                        command=lambda n=nombre: self._delete_category(n),
                        **btn_inline,
                    ).grid(row=0, column=1)

            self.after(0, _render)

        threading.Thread(target=_worker, daemon=True).start()

    def _add_category(self) -> None:
        """Add a new category from the quick-add form in the categories modal."""
        nombre = (getattr(self, "_new_cat_var", ctk.StringVar()).get() or "").strip()
        if not nombre:
            self._cat_error.configure(text="El nombre es obligatorio")
            return
        if nombre.lower() == "general":
            self._cat_error.configure(text="'General' ya existe por defecto")
            return
        try:
            ok = ConfiguracionService.add_category(nombre)
            if ok:
                self._cat_error.configure(text="")
                try:
                    self._new_cat_var.set("")
                except Exception:
                    pass
                self._load_categories_list()
                self._refresh_other_views()
            else:
                self._cat_error.configure(text="No se pudo agregar (posible duplicado)")
        except Exception as e:
            self._cat_error.configure(text=f"Error al agregar: {e}")

    def _rename_category_prompt(self, old_name: str) -> None:
        dlg, frame = create_modal(self, f"Renombrar '{old_name}'")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=f"Nuevo nombre para '{old_name}':").grid(
            row=0, column=0, sticky="w"
        )
        new_var = ctk.StringVar()
        ctk.CTkEntry(frame, textvariable=new_var, height=ENTRY_HEIGHT).grid(
            row=1, column=0, sticky="ew", pady=8
        )
        err = ctk.CTkLabel(frame, text="", text_color=ERROR_TEXT_RED)
        err.grid(row=2, column=0, sticky="ew")

        def do_rename():
            new_name = (new_var.get() or "").strip()
            if not new_name:
                err.configure(text="El nombre es obligatorio")
                return
            if old_name.lower() == "general":
                err.configure(text="No se puede renombrar 'General'")
                return
            try:
                ok = ConfiguracionService.rename_category(old_name, new_name)
                if ok:
                    dlg.destroy()
                    self._load_categories_list()
                    self._refresh_other_views()
                else:
                    err.configure(text="No se pudo renombrar (protegido o error)")
            except Exception as e:
                err.configure(text=f"Error al renombrar: {e}")

        base = get_content_button_style()
        btns = ctk.CTkFrame(frame, fg_color=WHITE)
        btns.grid(row=3, column=0, sticky="e", pady=(8, 0))
        ctk.CTkButton(btns, text="Cancelar", command=dlg.destroy, **base).grid(
            row=0, column=1, padx=(8, 0)
        )
        ctk.CTkButton(btns, text="Guardar", command=do_rename, **base).grid(
            row=0, column=0
        )

    def _delete_category(self, name: str) -> None:
        if name.lower() == "general":
            self._cat_error.configure(text="'General' no se puede eliminar")
            return
        if not messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar categoría '{name}' y reasignar sus productos a 'General'?",
        ):
            return
        try:
            ok = ConfiguracionService.delete_category(name)
            if ok:
                self._cat_error.configure(text="")
                self._load_categories_list()
                self._refresh_other_views()
            else:
                self._cat_error.configure(
                    text="No se pudo eliminar (protegido o error)"
                )
        except Exception as e:
            self._cat_error.configure(text=f"Error al eliminar: {e}")
