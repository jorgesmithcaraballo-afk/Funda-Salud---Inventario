import customtkinter as ctk
from PIL import Image
from resource.icons import get_icon
from resource.colors import (
    PRIMARY_BLUE,
    SECONDARY_BLUE,
    SECONDARY_BLUE_HOVER,
    WHITE,
    ERROR_RED,
    get_content_button_style,
)
from resource.sizes import ENTRY_HEIGHT
from resource.strings import (
    LOGIN_TITLE,
    LOGIN_USERNAME_PLACEHOLDER,
    LOGIN_PASSWORD_PLACEHOLDER,
    LOGIN_SHOW_PASSWORD,
    LOGIN_BUTTON,
    LOGIN_ERROR_EMPTY,
    LOGIN_ERROR_USERNAME_FORMAT,
    LOGIN_ERROR_USERNAME_TOO_LONG,
    LOGIN_ERROR_PASSWORD_TOO_LONG,
)
import os
import logging
import threading
from tkinter import messagebox
from typing import Any, Optional
from services.application.login_service import LoginService
import re


LOGO_PATH = os.path.join("img", "logo.png")


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

    def _handle_auth_result(
        self,
        ok: bool,
        usuario: str,
        err: Optional[Exception],
        row: Optional[dict] = None,
    ) -> None:
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
                        "id": row.get("id"),
                        "nombre": row.get("nombre"),
                        "tipo": (row.get("tipo") or "user"),
                    }
                else:
                    # Fallback mínimo
                    self.controlador.current_user = {
                        "id": None,
                        "nombre": usuario,
                        "tipo": "user",
                    }
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
                self.progress_bar.pack(pady=(10, 0), fill="x")
                self.progress_bar.start()
                self.progress_visible = True
        else:
            if self.progress_visible:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                self.progress_visible = False

    def _inputs_validos(self) -> bool:
        usuario = self.username.get().strip()
        clave = self.password.get().strip()
        if not usuario or not clave:
            self.error_label.configure(text=LOGIN_ERROR_EMPTY)
            return False
        # Validar que el usuario contenga solo letras y números (sin espacios)
        if not re.fullmatch(r"[A-Za-z0-9]+", usuario):
            self.error_label.configure(text=LOGIN_ERROR_USERNAME_FORMAT)
            return False
        # Límites de longitud
        if len(usuario) > 32:
            self.error_label.configure(text=LOGIN_ERROR_USERNAME_TOO_LONG)
            return False
        if len(clave) > 128:
            self.error_label.configure(text=LOGIN_ERROR_PASSWORD_TOO_LONG)
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

        hilo = threading.Thread(
            target=self._auth_worker, args=(usuario, clave), daemon=True
        )
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

        # --- Configuración del Grid Responsivo ---
        self.configure(fg_color="white")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        # --- Paneles con Grid ---
        # Panel izquierdo para el formulario
        self.form_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.form_panel.grid(row=0, column=0, sticky="nsew")
        self.form_panel.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)
        self.form_panel.grid_columnconfigure(0, weight=1)

        # Panel derecho para el logo
        self.logo_panel = ctk.CTkFrame(self, fg_color=PRIMARY_BLUE)
        self.logo_panel.grid(row=0, column=1, sticky="nsew")
        self.logo_panel.grid_rowconfigure(0, weight=1)
        self.logo_panel.grid_columnconfigure(0, weight=1)

        # Construir UI
        self._build_form()
        self._build_logo()
        self._bind_events()

    def _build_form(self) -> None:
        # Frame para centrar el contenido del formulario
        content = ctk.CTkFrame(self.form_panel, fg_color="transparent")
        content.grid(row=0, column=0, sticky="", pady=20, padx=20)
        # Centrar el frame en el panel
        self.form_panel.grid_rowconfigure(0, weight=1)

        title = ctk.CTkLabel(
            content,
            text=LOGIN_TITLE,
            compound="left",
            font=ctk.CTkFont(size=48, weight="bold"),
        )
        title.pack(pady=(0, 40))

        # Prefill username using StringVar (CTkEntry does not support 'text' kwarg)
        self._username_var = ctk.StringVar(value="deivys")
        self.username = ctk.CTkEntry(
            content,
            textvariable=self._username_var,
            placeholder_text=LOGIN_USERNAME_PLACEHOLDER,
            width=250,
            height=ENTRY_HEIGHT,
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

        # Prefill password using StringVar (masked by show='*')
        self._password_var = ctk.StringVar(value="deivys")
        self.password = ctk.CTkEntry(
            content,
            textvariable=self._password_var,
            placeholder_text=LOGIN_PASSWORD_PLACEHOLDER,
            show="*",
            width=250,
            height=ENTRY_HEIGHT,
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
            text=LOGIN_SHOW_PASSWORD,
            font=ctk.CTkFont(size=18),
            variable=self.show_pass_var,
            command=self.toggle_password,
        )
        toggle.pack(pady=(0, 10))

        # Mensaje de error discreto bajo los campos
        self.error_label = ctk.CTkLabel(
            content,
            text="",
            text_color=ERROR_RED,
            font=ctk.CTkFont(size=16, weight="normal"),
        )
        self.error_label.pack(pady=(0, 10))

        # Botón principal
        _btn_style = get_content_button_style()
        # Override only colors and font to keep brand look while unifying size
        _btn_style = {
            **_btn_style,
            "fg_color": SECONDARY_BLUE,
            "hover_color": SECONDARY_BLUE_HOVER,
            "text_color": WHITE,
            # Larger font for primary action in login while keeping same size
            "font": ctk.CTkFont(size=25, weight="bold"),
        }
        self.login_btn = ctk.CTkButton(
            content,
            text=LOGIN_BUTTON,
            command=self.on_submit,
            **_btn_style,
        )
        self.login_btn.pack(pady=(5, 0))

        # Barra de progreso (oculta por defecto)
        self.progress_bar = ctk.CTkProgressBar(content, mode="indeterminate")
        self.progress_bar.set(0)

    def _build_logo(self) -> None:
        """Construye el panel de logo en el lado derecho."""
        try:
            logo_img = get_icon("logo", size=(250, 250))
            logo_label = ctk.CTkLabel(self.logo_panel, image=logo_img, text="")
            logo_label.grid(row=0, column=0, sticky="")
        except Exception:
            # Fallback a ruta clásica si hay problema con icons
            try:
                logo_big = ctk.CTkImage(Image.open(LOGO_PATH), size=(250, 250))
                logo_label = ctk.CTkLabel(self.logo_panel, image=logo_big, text="")
                logo_label.grid(row=0, column=0, sticky="")
            except Exception:
                logo_label = ctk.CTkLabel(self.logo_panel, text="(logo)")
                logo_label.grid(row=0, column=0, sticky="")

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
