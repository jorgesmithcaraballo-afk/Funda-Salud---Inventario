import customtkinter as ctk
from PIL import Image
from components.layout import BaseLayout
from colors import (PRIMARY_BLUE, BUTTON_PRIMARY_BG, BUTTON_PRIMARY_HOVER, BUTTON_PRIMARY_TEXT)
import os
import mysql.connector
from tkinter import messagebox
from typing import Any


LOGO_PATH = os.path.join("img", "logo.png")


class LoginView(ctk.CTkFrame):
    # -- funtions --
    def verificar_credenciales(self) -> None:
        usuario = self.username.get()
        clave = self.password.get()

        try:
            # Use context manager for safe connection handling
            from db_utils import ConnectionManager, QueryExecutor
            
            # Login query
            consulta = "SELECT * FROM personal WHERE nombre = %s AND contrasena = %s"
            resultado = QueryExecutor.execute_query(
                consulta, 
                params=(usuario, clave), 
                fetch_one=True
            )

            if resultado:
                print(f"✅ Login exitoso para usuario: {usuario}")
                self.controlador.mostrar_vista("filtro")
            else:
                print(f"❌ Credenciales incorrectas")
                messagebox.showerror(
                    "Acceso denegado", 
                    "Usuario o contraseña incorrectos"
                )

        except Exception as err:
            print(f"❌ Error de conexión en login: {err}")
            import logging
            logging.error(f"Login error: {err}")
            messagebox.showerror(
                "Error de conexión", 
                f"No se pudo conectar a la base de datos:\n{err}"
            )

    def toggle_password(self) -> None:
        self.password.configure(show="" if self.show_pass_var.get() else "*")

    # --- main ---
    def __init__(self, master: Any, controlador: Any):
        super().__init__(master)
        self.controlador = controlador  # Referencia al App para cambiar vistas

        layout = BaseLayout(self, azul_hex=PRIMARY_BLUE)
        layout.pack(fill="both", expand=True)

        form = layout.left_panel
        logo_panel = layout.right_panel

        content = ctk.CTkFrame(form, fg_color="transparent")
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
        toggle.pack(pady=(0, 30))

        login_btn = ctk.CTkButton(
            content,
            text="Acceder",
            fg_color=BUTTON_PRIMARY_BG,
            hover_color=BUTTON_PRIMARY_HOVER,
            text_color=BUTTON_PRIMARY_TEXT,
            font=ctk.CTkFont(size=35),
            command=self.verificar_credenciales,
        )
        login_btn.pack()

        try:
            logo_big = ctk.CTkImage(Image.open(LOGO_PATH), size=(250, 250))
            ctk.CTkLabel(logo_panel, image=logo_big, text="").place(
                relx=0.5, rely=0.5, anchor="center"
            )
        except:
            ctk.CTkLabel(logo_panel, text="(logo)").place(
                relx=0.5, rely=0.5, anchor="center"
            )
