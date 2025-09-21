import customtkinter as ctk


class BaseLayout(ctk.CTkFrame):
    def __init__(self, master, azul_hex="#004aad", **kwargs):
        super().__init__(master, **kwargs)

        self.left_panel = ctk.CTkFrame(
            self, fg_color="white", width=400, corner_radius=0
        )
        self.left_panel.pack(side="left", fill="both", expand=True)

        self.right_panel = ctk.CTkFrame(
            self, fg_color=azul_hex, width=400, corner_radius=0
        )
        self.right_panel.pack(side="right", fill="both", expand=False)
