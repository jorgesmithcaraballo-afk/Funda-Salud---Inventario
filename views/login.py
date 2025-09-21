from config import AZUL_PRIMARIO
import customtkinter as ctk
from PIL import Image
from components.layout import BaseLayout
import os
import mysql.connector
from tkinter import messagebox


LOGO_PATH = os.path.join("img", "logo.png")


class LoginView(ctk.CTkFrame):
    # -- funtions --
    def verificar_credenciales(self):
        usuario = self.username.get()
        clave = self.password.get()

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="fs",
                password="Gato7Sol",
                database="sistema_inventario",
            )
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM personal WHERE nombre = %s AND contrasena = %s",
                (usuario, clave),
            )
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                self.controlador.mostrar_vista("filtro")
            else:
                messagebox.showerror(
                    "Acceso denegado", "Usuario o contraseña incorrectos"
                )

        except mysql.connector.Error as err:
            messagebox.showerror(
                "Error de conexión", f"No se pudo conectar a la base de datos:\n{err}"
            )

    def toggle_password(self):
        self.password.configure(show="" if self.show_pass_var.get() else "*")

    # --- main ---
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador  # Referencia al App para cambiar vistas

        layout = BaseLayout(self, azul_hex=AZUL_PRIMARIO)
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
            fg_color=AZUL_PRIMARIO,
            hover_color="#00367d",
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
