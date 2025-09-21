import customtkinter as ctk


class ChatView(ctk.CTkFrame):
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador

        label = ctk.CTkLabel(
            self, text="ChatView", font=ctk.CTkFont(size=36, weight="bold")
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
