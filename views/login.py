import customtkinter as ctk
from PIL import Image
from components.layout import BaseLayout
from resource.colors import (PRIMARY_BLUE, BUTTON_PRIMARY_BG, BUTTON_PRIMARY_HOVER, BUTTON_PRIMARY_TEXT)
import os
import logging
import threading
from tkinter import messagebox
from typing import Any, Optional
import hashlib
import os as _os


LOGO_PATH = os.path.join("img", "logo.png")


class LoginView(ctk.CTkFrame):
    # --- Configuración de logging ---
    _logger = logging.getLogger(__name__)

    # --- Lógica de autenticación (interna a este archivo) ---
    def _hash_password(self, password: str, iterations: int = 100_000) -> str:
        """Genera hash seguro PBKDF2-HMAC-SHA256 con salt aleatoria.
        Formato almacenado: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
        """
        salt = _os.urandom(16)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

    def _verify_password(self, password: str, stored: str) -> bool:
        """Verifica contraseña contra hash almacenado o texto plano (legacy)."""
        try:
            if stored and '$' in stored:
                algo, iter_s, salt_hex, hash_hex = stored.split('$', 3)
                if algo != 'pbkdf2_sha256':
                    return False
                iterations = int(iter_s)
                salt = bytes.fromhex(salt_hex)
                expected = bytes.fromhex(hash_hex)
                dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
                return dk == expected
            # Legacy: texto plano
            return password == stored
        except Exception:
            return False

    def _auth_worker(self, usuario: str, clave: str) -> None:
        """Ejecuta la verificación de credenciales en segundo plano."""
        try:
            from db_utils import QueryExecutor  # Mantener dependencia interna

            # Buscar por nombre y verificar contraseña localmente (soporta hash/legacy)
            consulta = "SELECT * FROM personal WHERE nombre = %s LIMIT 1"
            row = QueryExecutor.execute_query(
                consulta,
                params=(usuario,),
                fetch_one=True,
            )

            ok = False
            upgraded = False
            if row:
                stored = row.get('contrasena')
                ok = self._verify_password(clave, stored)
                # Si fue legacy y coincide, actualizar a hash seguro
                if ok and (stored is None or '$' not in stored):
                    try:
                        new_hash = self._hash_password(clave)
                        QueryExecutor.execute_query(
                            "UPDATE personal SET contrasena = %s WHERE id = %s",
                            params=(new_hash, row.get('id')),
                            fetch_one=False,
                            fetch_all=False,
                        )
                        upgraded = True
                    except Exception:
                        pass

            # Regresar al hilo principal para actualizar UI con datos del usuario
            self.after(0, self._handle_auth_result, ok, usuario, None if ok or row is None else None, row)

        except Exception as err:  # Captura segura (DB/otros)
            self._logger.error(f"Login error: {err}")
            self.after(0, self._handle_auth_result, False, usuario, err, None)

    def _handle_auth_result(self, ok: bool, usuario: str, err: Optional[Exception], row: Optional[dict] = None) -> None:
        """Actualiza la UI según el resultado de autenticación."""
        self._set_loading_state(False)

        if err is not None:
            messagebox.showerror(
                "Error de conexión",
                f"No se pudo conectar a la base de datos:\n{err}",
            )
            self.error_label.configure(text="Error de conexión. Intenta de nuevo.")
            return

        if ok:
            self._logger.info(f"Login exitoso para usuario: {usuario}")
            self.error_label.configure(text="")
            # Guardar usuario actual para control de permisos en otras vistas
            try:
                if row:
                    self.controlador.current_user = {
                        'id': row.get('id'),
                        'nombre': row.get('nombre'),
                        'tipo': (row.get('tipo') or 'user')
                    }
                else:
                    # Fallback mínimo
                    self.controlador.current_user = {'id': None, 'nombre': usuario, 'tipo': 'user'}
            except Exception:
                pass
            self.controlador.mostrar_vista("filtro")
        else:
            self._logger.warning("Credenciales incorrectas")
            self.error_label.configure(text="Usuario o contraseña incorrectos")

    # --- Utilidades de UI ---
    def _set_loading_state(self, loading: bool) -> None:
        """Habilita/inhabilita controles y muestra progreso durante el login."""
        state = "disabled" if loading else "normal"
        try:
            self.username.configure(state=state)
            self.password.configure(state=state)
            self.login_btn.configure(state=state)
        except Exception:
            pass

        # Indicador de progreso
        if loading:
            if not self.progress_visible:
                self.progress_bar.place(relx=0.5, rely=1.0, anchor="s", y=10)
                self.progress_bar.start()
                self.progress_visible = True
        else:
            if self.progress_visible:
                self.progress_bar.stop()
                self.progress_bar.place_forget()
                self.progress_visible = False

    def _inputs_validos(self) -> bool:
        usuario = self.username.get().strip()
        clave = self.password.get().strip()
        if not usuario or not clave:
            self.error_label.configure(text="Ingresa usuario y contraseña")
            return False
        self.error_label.configure(text="")
        return True

    # --- Eventos ---
    def on_submit(self) -> None:
        """Valida y lanza autenticación en un hilo para no bloquear la UI."""
        if not self._inputs_validos():
            return

        usuario = self.username.get().strip()
        clave = self.password.get().strip()
        self._set_loading_state(True)

        hilo = threading.Thread(target=self._auth_worker, args=(usuario, clave), daemon=True)
        hilo.start()

    def toggle_password(self) -> None:
        self.password.configure(show="" if self.show_pass_var.get() else "*")

    # --- Construcción de UI ---
    def __init__(self, master: Any, controlador: Any):
        super().__init__(master)
        self.controlador = controlador  # Referencia al App para cambiar vistas

        # Estado UI
        self.progress_visible = False

        # Layout base (mantener consistencia con diseño actual)
        layout = BaseLayout(self, azul_hex=PRIMARY_BLUE)
        layout.pack(fill="both", expand=True)

        self.form_panel = layout.left_panel
        self.logo_panel = layout.right_panel

        # Construir UI
        self._build_form()
        self._build_logo()
        self._bind_events()

    def _build_form(self) -> None:
        content = ctk.CTkFrame(self.form_panel, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            content,
            text=" Inicia Sesión",
            compound="left",
            font=ctk.CTkFont(size=48, weight="bold"),
        )
        title.pack(pady=(0, 40))

        self.username = ctk.CTkEntry(
            content,
            placeholder_text="Nombre de usuario",
            width=250,
            font=ctk.CTkFont(size=25),
        )
        self.username.pack(pady=(0, 15))

        self.show_pass_var = ctk.BooleanVar(value=False)

        self.password = ctk.CTkEntry(
            content,
            placeholder_text="Contraseña",
            show="*",
            width=250,
            font=ctk.CTkFont(size=25),
        )
        self.password.pack(pady=(0, 5))

        toggle = ctk.CTkCheckBox(
            content,
            text="Mostrar contraseña",
            font=ctk.CTkFont(size=18),
            variable=self.show_pass_var,
            command=self.toggle_password,
        )
        toggle.pack(pady=(0, 10))

        # Mensaje de error discreto bajo los campos
        self.error_label = ctk.CTkLabel(
            content,
            text="",
            text_color="#cc0000",
            font=ctk.CTkFont(size=16, weight="normal"),
        )
        self.error_label.pack(pady=(0, 10))

        # Botón principal
        self.login_btn = ctk.CTkButton(
            content,
            text="Acceder",
            fg_color=BUTTON_PRIMARY_BG,
            hover_color=BUTTON_PRIMARY_HOVER,
            text_color=BUTTON_PRIMARY_TEXT,
            font=ctk.CTkFont(size=35),
            command=self.on_submit,
        )
        self.login_btn.pack(pady=(5, 0))

        # Barra de progreso (oculta por defecto)
        self.progress_bar = ctk.CTkProgressBar(content, mode="indeterminate")
        self.progress_bar.set(0)

    def _build_logo(self) -> None:
        try:
            logo_big = ctk.CTkImage(Image.open(LOGO_PATH), size=(250, 250))
            ctk.CTkLabel(self.logo_panel, image=logo_big, text="").place(
                relx=0.5, rely=0.5, anchor="center"
            )
        except Exception:
            ctk.CTkLabel(self.logo_panel, text="(logo)").place(
                relx=0.5, rely=0.5, anchor="center"
            )

    def _bind_events(self) -> None:
        # Enter para enviar
        self.username.bind("<Return>", lambda _: self.on_submit())
        self.password.bind("<Return>", lambda _: self.on_submit())

