import customtkinter as ctk


class ConfiguracionView(ctk.CTkFrame):
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador

        label = ctk.CTkLabel(
            self, text="Configuración", font=ctk.CTkFont(size=36, weight="bold")
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
