import customtkinter as ctk
from resource.colors import (VIEW_BACKGROUND, HEADER_BG, HEADER_TEXT, LIGHT_GRAY, 
                   TEXT_PRIMARY, TEXT_SECONDARY, get_header_button_style)
from resource.icons import *
from resource.strings import CONFIG_TITLE
from typing import Any
from tkinter import messagebox
import logging
import hashlib
import os as _os


class ConfiguracionView(ctk.CTkFrame):
    def __init__(self, master: Any, controlador: Any):
        super().__init__(master)
        self.controlador = controlador
        self.previous_view = "filtro"  # Default previous view
        
        # Main background
        self.configure(fg_color=VIEW_BACKGROUND)
        
        # Header with back button
        header_frame = ctk.CTkFrame(self, fg_color=HEADER_BG, height=70)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Back button (left)
        back_button_style = get_header_button_style()
        self.back_button = ctk.CTkButton(
            header_content,
            text=ICON_BACK_ARROW,
            command=self.go_back,
            **back_button_style
        )
        self.back_button.pack(side="left", anchor="w")
        
        # Title (center)
        title_label = ctk.CTkLabel(
            header_content,
            text=f"{ICON_SETTINGS} {CONFIG_TITLE}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=HEADER_TEXT
        )
        title_label.pack(side="left", expand=True, padx=(20, 0))
        
        # Header queda solo con botón atrás y título; acciones irán en options_frame
        
        # Main content area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Configuration options placeholder
        config_label = ctk.CTkLabel(
            content_frame,
            text="⚙️ Configuración del Sistema",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        config_label.pack(pady=(20, 40))
        
        # Add some configuration options
        options_frame = ctk.CTkFrame(content_frame, fg_color=LIGHT_GRAY, corner_radius=10)
        options_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # Toolbar de acciones dentro de options_frame
        actions_bar = ctk.CTkFrame(options_frame, fg_color="transparent")
        actions_bar.pack(fill="x", pady=(0, 16))

        btn_style = get_header_button_style()
        self.manage_users_btn = ctk.CTkButton(
            actions_bar,
            text="👤 Gestionar usuarios",
            command=self.open_manage_users_modal,
            **btn_style
        )
        self.manage_users_btn.pack(side="left")

        self.add_user_btn = ctk.CTkButton(
            actions_bar,
            text="➕ Agregar usuario",
            command=self.open_add_user_modal,
            **btn_style
        )
        self.add_user_btn.pack(side="left", padx=(8, 0))

        # Gestión de categorías
        self.manage_cats_btn = ctk.CTkButton(
            actions_bar,
            text="🏷️ Categorías",
            command=self.open_manage_categories_modal,
            **btn_style
        )
        self.manage_cats_btn.pack(side="left", padx=(8, 0))
        
        # Logger
        self._logger = logging.getLogger(__name__)
    
    def set_previous_view(self, view_name: str) -> None:
        """Set the previous view for navigation"""
        self.previous_view = view_name
    
    def go_back(self) -> None:
        """Go back to previous view"""
        try:
            print(f"🔙 Regresando a vista: {self.previous_view}")
            self.controlador.mostrar_vista(self.previous_view)
        except Exception as e:
            print(f"❌ Error regresando a vista anterior: {e}")
            # Fallback to filtro
            self.controlador.mostrar_vista("filtro")

    # ------------------
    # Modal: Agregar usuario
    # ------------------
    def _hash_password(self, password: str, iterations: int = 100_000) -> str:
        """Genera hash seguro PBKDF2-HMAC-SHA256 (igual esquema que login)."""
        salt = _os.urandom(16)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

    def open_add_user_modal(self) -> None:
        """Abre un modal para crear un nuevo usuario en la tabla 'personal'."""
        # Evitar múltiples instancias
        if hasattr(self, "_add_user_win") and self._add_user_win is not None and self._add_user_win.winfo_exists():
            try:
                self._add_user_win.focus_set()
            except Exception:
                pass
            return

        win = ctk.CTkToplevel(self)
        win.title("Agregar usuario")
        win.geometry("480x520")
        win.transient(self.winfo_toplevel())
        win.grab_set()
        self._add_user_win = win

        container = ctk.CTkFrame(win)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        # Variables de formulario
        self._nombre_var = ctk.StringVar()
        self._apellido_var = ctk.StringVar()
        self._contrasena_var = ctk.StringVar()
        self._contrasena2_var = ctk.StringVar()
        self._tipo_var = ctk.StringVar(value="user")

        # Helper para fila
        def add_field(parent, label_text, widget):
            group = ctk.CTkFrame(parent, fg_color="transparent")
            group.pack(fill="x", pady=8)
            ctk.CTkLabel(group, text=label_text, anchor="w").pack(fill="x", pady=(0, 4))
            widget.pack(fill="x")

        # Campos (vertical)
        add_field(container, "Nombre", ctk.CTkEntry(container, textvariable=self._nombre_var))
        add_field(container, "Apellido", ctk.CTkEntry(container, textvariable=self._apellido_var))
        add_field(container, "Contraseña", ctk.CTkEntry(container, textvariable=self._contrasena_var, show="*"))
        add_field(container, "Confirmar contraseña", ctk.CTkEntry(container, textvariable=self._contrasena2_var, show="*"))

        tipo_menu = ctk.CTkOptionMenu(container, variable=self._tipo_var, values=["admin", "user"])
        add_field(container, "Tipo", tipo_menu)

        # Mensaje de error
        self._error_label = ctk.CTkLabel(container, text="", text_color="#cc0000")
        self._error_label.pack(pady=(8, 0))

        # Botones
        btns = ctk.CTkFrame(container, fg_color="transparent")
        btns.pack(fill="x", pady=8)
        ctk.CTkButton(btns, text="Cancelar", command=win.destroy).pack(side="right")
        self._save_btn = ctk.CTkButton(btns, text="Guardar", command=self._save_new_user)
        self._save_btn.pack(side="right", padx=(0, 8))

        # Foco inicial
        try:
            win.after(100, lambda: win.focus())
        except Exception:
            pass

    def _validate_user_form(self) -> bool:
        nombre = (self._nombre_var.get() or "").strip()
        apellido = (self._apellido_var.get() or "").strip()
        contrasena = (self._contrasena_var.get() or "").strip()
        contrasena2 = (self._contrasena2_var.get() or "").strip()
        tipo = (self._tipo_var.get() or "").strip().lower()

        if not nombre or not apellido or not contrasena:
            self._error_label.configure(text="Nombre, Apellido y Contraseña son obligatorios")
            return False
        if tipo not in ("admin", "user"):
            self._error_label.configure(text="Tipo inválido. Usa admin o user")
            return False
        if not (5 <= len(contrasena) <= 8):
            self._error_label.configure(text="La contraseña debe tener entre 5 y 8 caracteres")
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
        tiempo_int = None

        # Deshabilitar botón mientras se guarda
        try:
            self._save_btn.configure(state="disabled")
        except Exception:
            pass

        try:
            from db_utils import QueryExecutor
            # Nota: Usamos placeholders estilo MySQL (%s)
            query = (
                "INSERT INTO personal (nombre, apellido, tiempo, contrasena, tipo) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            # Hash de contraseña antes de guardar
            hashed = self._hash_password(contrasena)
            params = (nombre, apellido, tiempo_int, hashed, tipo)
            affected = QueryExecutor.execute_query(query, params=params, fetch_one=False, fetch_all=False)

            if affected and affected > 0:
                messagebox.showinfo("Usuario", "Usuario creado correctamente")
                if hasattr(self, "_add_user_win") and self._add_user_win is not None:
                    self._add_user_win.destroy()
                    self._add_user_win = None
            else:
                messagebox.showwarning("Usuario", "No se pudo crear el usuario. Intenta nuevamente")
        except Exception as e:
            self._logger = getattr(self, "_logger", logging.getLogger(__name__))
            self._logger.error(f"Error creando usuario: {e}")
            messagebox.showerror("Error", f"No se pudo crear el usuario:\n{e}")
        finally:
            try:
                self._save_btn.configure(state="normal")
            except Exception:
                pass

    # ------------------
    # Modal: Gestionar usuarios (listar/editar/eliminar)
    # ------------------
    def open_manage_users_modal(self) -> None:
        if hasattr(self, "_manage_win") and self._manage_win is not None and self._manage_win.winfo_exists():
            try:
                self._manage_win.focus_set()
            except Exception:
                pass
            return

        win = ctk.CTkToplevel(self)
        win.title("Gestionar usuarios")
        win.geometry("700x480")
        win.transient(self.winfo_toplevel())
        win.grab_set()
        self._manage_win = win

        container = ctk.CTkFrame(win)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        # Encabezados
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))
        for text, w in [("ID", 60), ("Nombre", 150), ("Apellido", 150), ("Tiempo", 80), ("Tipo", 80), ("Acciones", 120)]:
            ctk.CTkLabel(header, text=text, width=w, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")

        self._users_scroll = ctk.CTkScrollableFrame(container, fg_color=LIGHT_GRAY)
        self._users_scroll.pack(fill="both", expand=True)

        # Cargar usuarios
        self._load_users_list()

    def _load_users_list(self) -> None:
        # Limpiar
        for w in self._users_scroll.winfo_children():
            w.destroy()

        try:
            from db_utils import QueryExecutor
            rows = QueryExecutor.execute_query(
                "SELECT id, nombre, apellido, tiempo, tipo FROM personal ORDER BY id ASC",
                fetch_all=True
            ) or []
        except Exception as e:
            self._logger.error(f"Error cargando usuarios: {e}")
            rows = []

        for row in rows:
            rframe = ctk.CTkFrame(self._users_scroll, fg_color="white")
            rframe.pack(fill="x", pady=4, padx=4)
            ctk.CTkLabel(rframe, text=str(row.get('id')), width=60, anchor="w").pack(side="left")
            ctk.CTkLabel(rframe, text=row.get('nombre') or '', width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(rframe, text=row.get('apellido') or '', width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(rframe, text=str(row.get('tiempo') if row.get('tiempo') is not None else ''), width=80, anchor="w").pack(side="left")
            ctk.CTkLabel(rframe, text=row.get('tipo') or 'user', width=80, anchor="w").pack(side="left")

            actions = ctk.CTkFrame(rframe, fg_color="transparent")
            actions.pack(side="right")
            ctk.CTkButton(actions, text="Editar", width=70, command=lambda r=row: self._open_edit_user_modal(r)).pack(side="left", padx=4)
            ctk.CTkButton(actions, text="Eliminar", width=70, fg_color="#c0392b", hover_color="#a93226", command=lambda r=row: self._delete_user(r)).pack(side="left")

    def _open_edit_user_modal(self, row: dict) -> None:
        win = ctk.CTkToplevel(self)
        win.title(f"Editar usuario #{row.get('id')}")
        win.geometry("480x480")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        container = ctk.CTkFrame(win)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        nombre_var = ctk.StringVar(value=row.get('nombre') or '')
        apellido_var = ctk.StringVar(value=row.get('apellido') or '')
        contrasena_var = ctk.StringVar(value="")  # Vacío: no cambiar
        tipo_var = ctk.StringVar(value=row.get('tipo') or 'user')

        def add_field(parent, label_text, widget):
            group = ctk.CTkFrame(parent, fg_color="transparent")
            group.pack(fill="x", pady=8)
            ctk.CTkLabel(group, text=label_text, anchor="w").pack(fill="x", pady=(0, 4))
            widget.pack(fill="x")

        add_field(container, "Nombre", ctk.CTkEntry(container, textvariable=nombre_var))
        add_field(container, "Apellido", ctk.CTkEntry(container, textvariable=apellido_var))
        add_field(container, "Nueva contraseña", ctk.CTkEntry(container, textvariable=contrasena_var, show="*"))
        # Tipo: bloquear para 'naila'
        is_naila = (row.get('nombre') or '').strip().lower() == 'naila'
        if is_naila:
            # Mostrar el tipo como label no editable
            tipo_display = ctk.CTkLabel(container, text=row.get('tipo') or 'user')
            add_field(container, "Tipo", tipo_display)
        else:
            tipo_menu = ctk.CTkOptionMenu(container, variable=tipo_var, values=["admin", "user"])
            add_field(container, "Tipo", tipo_menu)

        error_label = ctk.CTkLabel(container, text="", text_color="#cc0000")
        error_label.pack(pady=(8, 0))

        def validate() -> bool:
            if not (nombre_var.get() or '').strip():
                error_label.configure(text="Nombre es obligatorio")
                return False
            if not (apellido_var.get() or '').strip():
                error_label.configure(text="Apellido es obligatorio")
                return False
            if not is_naila:
                t = (tipo_var.get() or '').strip().lower()
                if t not in ("admin", "user"):
                    error_label.configure(text="Tipo inválido")
                    return False
            if (contrasena_var.get() or '') and not (5 <= len(contrasena_var.get()) <= 8):
                error_label.configure(text="La nueva contraseña debe tener entre 5 y 8 caracteres")
                return False
            error_label.configure(text="")
            return True

        def save_changes() -> None:
            if not validate():
                return
            nombre = nombre_var.get().strip()
            apellido = apellido_var.get().strip()
            npass = (contrasena_var.get() or '').strip()
            # Si no es naila, tomamos tipo del selector; si es naila, conservamos el original
            tipo = (row.get('tipo') or 'user') if is_naila else (tipo_var.get() or 'user')
            tipo = (tipo or 'user').strip().lower()

            try:
                from db_utils import QueryExecutor
                if npass:
                    hashed = self._hash_password(npass)
                    QueryExecutor.execute_query(
                        "UPDATE personal SET nombre=%s, apellido=%s, tipo=%s, contrasena=%s WHERE id=%s",
                        params=(nombre, apellido, tipo, hashed, row.get('id')),
                        fetch_one=False, fetch_all=False
                    )
                else:
                    QueryExecutor.execute_query(
                        "UPDATE personal SET nombre=%s, apellido=%s, tipo=%s WHERE id=%s",
                        params=(nombre, apellido, tipo, row.get('id')),
                        fetch_one=False, fetch_all=False
                    )
                messagebox.showinfo("Usuario", "Cambios guardados")
                win.destroy()
                self._load_users_list()
            except Exception as e:
                self._logger.error(f"Error guardando cambios: {e}")
                messagebox.showerror("Error", f"No se pudo guardar cambios:\n{e}")

        btns = ctk.CTkFrame(container, fg_color="transparent")
        btns.pack(fill="x", pady=12)
        ctk.CTkButton(btns, text="Cancelar", command=win.destroy).pack(side="right")
        ctk.CTkButton(btns, text="Guardar", command=save_changes).pack(side="right", padx=(0, 8))

    def _delete_user(self, row: dict) -> None:
        uid = row.get('id')
        nombre = (row.get('nombre') or '').strip()
        tipo = (row.get('tipo') or 'user').strip().lower()
        # Protección: no permitir eliminar admin principal (naila)
        if tipo == 'admin' and nombre.lower() == 'naila':
            messagebox.showwarning("Protegido", "No se puede eliminar el admin principal (naila)")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar usuario #{uid} ({nombre})?"):
            return
        try:
            from db_utils import QueryExecutor
            QueryExecutor.execute_query(
                "DELETE FROM personal WHERE id = %s",
                params=(uid,),
                fetch_one=False,
                fetch_all=False
            )
            messagebox.showinfo("Usuario", "Usuario eliminado")
            self._load_users_list()
        except Exception as e:
            self._logger.error(f"Error eliminando usuario: {e}")
            messagebox.showerror("Error", f"No se pudo eliminar usuario:\n{e}")
            return

    # ------------------
    # Modal: Gestionar categorías
    # ------------------
    def open_manage_categories_modal(self) -> None:
        if hasattr(self, "_cats_win") and self._cats_win is not None and self._cats_win.winfo_exists():
            try:
                self._cats_win.focus_set()
            except Exception:
                pass
            return

        win = ctk.CTkToplevel(self)
        win.title("Gestionar categorías")
        win.geometry("560x520")
        win.transient(self.winfo_toplevel())
        win.grab_set()
        self._cats_win = win

        container = ctk.CTkFrame(win)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        # Alta rápida
        add_frame = ctk.CTkFrame(container, fg_color="transparent")
        add_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(add_frame, text="Nueva categoría").pack(side="left")
        self._new_cat_var = ctk.StringVar()
        ctk.CTkEntry(add_frame, textvariable=self._new_cat_var, width=260).pack(side="left", padx=8)
        ctk.CTkButton(add_frame, text="Agregar", command=self._add_category).pack(side="left")

        # Mensajes
        self._cat_error = ctk.CTkLabel(container, text="", text_color="#cc0000")
        self._cat_error.pack(fill="x", pady=(0, 6))

        # Listado
        self._cats_scroll = ctk.CTkScrollableFrame(container, fg_color=LIGHT_GRAY)
        self._cats_scroll.pack(fill="both", expand=True)
        self._load_categories_list()

    def _refresh_other_views(self) -> None:
        """Refresca vistas dependientes de categorías si existen en el controlador."""
        try:
            subir = getattr(self.controlador, 'frames', {}).get('subir')
            if subir and hasattr(subir, 'reset_view_state'):
                subir.reset_view_state()
        except Exception:
            pass
        try:
            filtro = getattr(self.controlador, 'frames', {}).get('filtro')
            if filtro and hasattr(filtro, 'reset_view_state'):
                filtro.reset_view_state()
        except Exception:
            pass

    def _load_categories_list(self) -> None:
        # Limpiar
        if not hasattr(self, "_cats_scroll"):
            return
        for w in self._cats_scroll.winfo_children():
            w.destroy()

        try:
            from db_utils import QueryExecutor
            # Asegurar catálogo y cargar
            QueryExecutor.execute_query(
                "CREATE TABLE IF NOT EXISTS categorias (nombre VARCHAR(50) PRIMARY KEY)",
                fetch_one=False, fetch_all=False
            )
            QueryExecutor.execute_query(
                "INSERT IGNORE INTO categorias (nombre) VALUES ('General')",
                fetch_one=False, fetch_all=False
            )
            rows = QueryExecutor.execute_query(
                "SELECT nombre FROM categorias ORDER BY nombre ASC",
                fetch_all=True
            ) or []
        except Exception as e2:
            self._cat_error.configure(text=f"Error cargando categorías: {e2}")
            rows = []

        if not rows:
            rows = [{'nombre': 'General'}]

        for r in rows:
            nombre = r.get('nombre') if isinstance(r, dict) else (r[0] if r else '')
            rowf = ctk.CTkFrame(self._cats_scroll, fg_color="white")
            rowf.pack(fill="x", pady=4, padx=4)
            ctk.CTkLabel(rowf, text=nombre, anchor="w").pack(side="left", padx=6)

            actions = ctk.CTkFrame(rowf, fg_color="transparent")
            actions.pack(side="right")
            ctk.CTkButton(actions, text="Renombrar", width=90, command=lambda n=nombre: self._rename_category_prompt(n)).pack(side="left", padx=4)
            ctk.CTkButton(actions, text="Eliminar", width=80, fg_color="#c0392b", hover_color="#a93226", command=lambda n=nombre: self._delete_category(n)).pack(side="left")

    def _add_category(self) -> None:
        nombre = (self._new_cat_var.get() or '').strip()
        if not nombre:
            self._cat_error.configure(text="El nombre es obligatorio")
            return
        if nombre.lower() == 'general':
            self._cat_error.configure(text="'General' ya existe por defecto")
            return
        # Crear en catálogo 'categorias'
        try:
            from db_utils import QueryExecutor
            QueryExecutor.execute_query(
                "CREATE TABLE IF NOT EXISTS categorias (nombre VARCHAR(50) PRIMARY KEY)",
                fetch_one=False, fetch_all=False
            )
            affected = QueryExecutor.execute_query(
                "INSERT IGNORE INTO categorias (nombre) VALUES (%s)",
                params=(nombre,), fetch_one=False, fetch_all=False
            )
            self._cat_error.configure(text="")
            self._new_cat_var.set("")
            self._load_categories_list()
            self._refresh_other_views()
        except Exception as e:
            self._cat_error.configure(text=f"Error al agregar: {e}")

    def _rename_category_prompt(self, old_name: str) -> None:
        dlg = ctk.CTkToplevel(self)
        dlg.title(f"Renombrar '{old_name}'")
        dlg.geometry("420x160")
        dlg.transient(self._cats_win)
        dlg.grab_set()
        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(frame, text=f"Nuevo nombre para '{old_name}':").pack(anchor="w")
        new_var = ctk.StringVar()
        ctk.CTkEntry(frame, textvariable=new_var).pack(fill="x", pady=8)
        err = ctk.CTkLabel(frame, text="", text_color="#cc0000")
        err.pack(fill="x")

        def do_rename():
            new_name = (new_var.get() or '').strip()
            if not new_name:
                err.configure(text="El nombre es obligatorio")
                return
            if old_name.lower() == 'general':
                err.configure(text="No se puede renombrar 'General'")
                return
            try:
                from db_utils import QueryExecutor
                # Asegurar catálogo y renombrar
                QueryExecutor.execute_query(
                    "CREATE TABLE IF NOT EXISTS categorias (nombre VARCHAR(50) PRIMARY KEY)",
                    fetch_one=False, fetch_all=False
                )
                QueryExecutor.execute_query(
                    "UPDATE categorias SET nombre=%s WHERE nombre=%s",
                    params=(new_name, old_name), fetch_one=False, fetch_all=False
                )
                QueryExecutor.execute_query(
                    "INSERT IGNORE INTO categorias (nombre) VALUES (%s)",
                    params=(new_name,), fetch_one=False, fetch_all=False
                )
                # Actualizar referencias en Inventario
                QueryExecutor.execute_query(
                    "UPDATE Inventario SET categoria=%s WHERE categoria=%s",
                    params=(new_name, old_name), fetch_one=False, fetch_all=False
                )
                dlg.destroy()
                self._load_categories_list()
                self._refresh_other_views()
            except Exception as e:
                err.configure(text=f"Error al renombrar: {e}")

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill="x", pady=(8, 0))
        ctk.CTkButton(btns, text="Cancelar", command=dlg.destroy).pack(side="right")
        ctk.CTkButton(btns, text="Guardar", command=do_rename).pack(side="right", padx=(0, 8))

    def _delete_category(self, name: str) -> None:
        if name.lower() == 'general':
            self._cat_error.configure(text="'General' no se puede eliminar")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar categoría '{name}' y reasignar sus productos a 'General'?"):
            return
        try:
            from db_utils import QueryExecutor
            # Reasignar en inventario
            QueryExecutor.execute_query(
                "UPDATE Inventario SET categoria='General' WHERE categoria=%s",
                params=(name,), fetch_one=False, fetch_all=False
            )
            # Eliminar del catálogo
            QueryExecutor.execute_query(
                "DELETE FROM categorias WHERE nombre=%s",
                params=(name,), fetch_one=False, fetch_all=False
            )
            self._cat_error.configure(text="")
            self._load_categories_list()
            self._refresh_other_views()
        except Exception as e:
            self._cat_error.configure(text=f"Error al eliminar: {e}")
