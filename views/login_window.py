import customtkinter as ctk
from PIL import Image
from components.layout import BaseLayout
from resource.colors import (PRIMARY_BLUE, BUTTON_PRIMARY_BG, BUTTON_PRIMARY_HOVER, BUTTON_PRIMARY_TEXT)
import os
import logging
import threading
from tkinter import messagebox
from typing import Any, Optional
from services.application.login_service import LoginService
import re
import sys

def get_resource_path(relative_path):
   """Obtiene la ruta absoluta al recurso, funciona en desarrollo y .exe"""
   try:
       # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
       base_path = sys._MEIPASS
   except Exception:
       base_path = os.path.abspath(".")
   return os.path.join(base_path, relative_path)

class LoginView(ctk.CTkFrame):
    # --- Configuración de logging ---
    _logger = logging.getLogger(__name__)

    def _auth_worker(self, usuario: str, clave: str) -> None:
        """Ejecuta la verificación de credenciales en segundo plano."""
        try:
            ok, row, err_msg = LoginService.authenticate(usuario, clave)
            # Regresar al hilo principal para actualizar UI con datos del usuario
            self.after(0, self._handle_auth_result, ok, usuario, err_msg, row)
        except Exception as err:
            self._logger.error(f"Login error: {err}")
            self.after(0, self._handle_auth_result, False, usuario, str(err), None)

    def _handle_auth_result(self, ok: bool, usuario: str, err: Optional[Exception], row: Optional[dict] = None) -> None:
        """Actualiza la UI según el resultado de autenticación."""
        self._set_loading_state(False)
        # Permitir nuevos intentos tras completar
        try:
            self._auth_in_progress = False
        except Exception:
            pass

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
        # Validar que el usuario contenga solo letras y números (sin espacios)
        if not re.fullmatch(r"[A-Za-z0-9]+", usuario):
            self.error_label.configure(text="El usuario solo puede contener letras y números")
            return False
        # Límites de longitud
        if len(usuario) > 32:
            self.error_label.configure(text="El usuario no puede exceder 32 caracteres")
            return False
        if len(clave) > 128:
            self.error_label.configure(text="La contraseña no puede exceder 128 caracteres")
            return False
        self.error_label.configure(text="")
        return True

    # --- Eventos ---
    def on_submit(self) -> None:
        """Valida y lanza autenticación en un hilo para no bloquear la UI."""
        if not self._inputs_validos():
            return
        # Evitar múltiples envíos simultáneos
        if getattr(self, "_auth_in_progress", False):
            return

        # Normalizar usuario a minúsculas para login case-insensitive
        usuario = self.username.get().strip().lower()
        clave = self.password.get().strip()
        self._set_loading_state(True)
        self._auth_in_progress = True

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
        self._auth_in_progress = False

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
        # Validación: permitir solo letras y números en tiempo de escritura
        try:
            vcmd = self.register(self._username_validate)
            self.username.configure(validate="key", validatecommand=(vcmd, "%P"))
        except Exception:
            # Si customtkinter no soporta validate, al menos quedará la validación en submit
            pass

        self.show_pass_var = ctk.BooleanVar(value=False)

        self.password = ctk.CTkEntry(
            content,
            placeholder_text="Contraseña",
            show="*",
            width=250,
            font=ctk.CTkFont(size=25),
        )
        self.password.pack(pady=(0, 5))
        # Límite de longitud en tiempo real para contraseña (hasta 128)
        try:
            pvcmd = self.register(self._password_validate)
            self.password.configure(validate="key", validatecommand=(pvcmd, "%P"))
        except Exception:
            pass

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
            logo_path = get_resource_path("app_resources/img/logo.png")
            logo_big = ctk.CTkImage(Image.open(logo_path), size=(250, 250))
            ctk.CTkLabel(self.logo_panel, image=logo_big, text="").place(
                relx=0.5, rely=0.5, anchor="center"
            )
        except Exception as e:
            print("Error cargando logo:", e)
            ctk.CTkLabel(self.logo_panel, text="(logo)").place(
                relx=0.5, rely=0.5, anchor="center"
            )


    def _bind_events(self) -> None:
        # Enter para enviar
        self.username.bind("<Return>", lambda _: self.on_submit())
        self.password.bind("<Return>", lambda _: self.on_submit())

    # --- Validadores ---
    def _username_validate(self, proposed: str) -> bool:
        """Permite solo letras y números en el campo de usuario (incluye vacío para borrar)."""
        try:
            # Solo alfanumérico y longitud máxima 32
            return bool(re.fullmatch(r"[A-Za-z0-9]{0,32}", proposed or ""))
        except Exception:
            return True

    def _password_validate(self, proposed: str) -> bool:
        """Limita la contraseña a 128 caracteres (se permiten especiales)."""
        try:
            return len(proposed or "") <= 128
        except Exception:
            return True

