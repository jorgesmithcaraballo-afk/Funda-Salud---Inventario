from configuracion import ConfiguracionView
from views.filtro import FiltroView
from views.login import LoginView
from views.subir import SubirView
from config import AZUL_PRIMARIO
from views.chat_ai import ChatAIView
from tkinter import filedialog
import customtkinter as ctk
import os


ICON_PATH = os.path.join("img", "icono.ico")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mi Aplicación")
        self.geometry("800x500")
        self.resizable(False, False)

        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)

        # Diccionario para almacenar las vistas
        self.frames = {}

        # Registro de vistas
        self.registrar_vista("login", LoginView)
        self.registrar_vista("filtro", FiltroView)
        self.registrar_vista("chat_ai", ChatAIView)
        self.registrar_vista("subir", SubirView)
        self.registrar_vista("configuracion", ConfiguracionView)

        # Mostrar la vista inicial
        self.mostrar_vista("login")

    def registrar_vista(self, nombre, clase_vista):
        frame = clase_vista(self, self)
        self.frames[nombre] = frame
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def mostrar_vista(self, nombre):
        # Cambiar tamaño según la vista
        if nombre == "filtro":
            self.geometry("1200x700")
        else:
            self.geometry("800x500")

        # Mostrar la vista
        for vista in self.frames.values():
            vista.lower()
        self.frames[nombre].lift()


if __name__ == "__main__":
    app = App()
    app.mainloop()
