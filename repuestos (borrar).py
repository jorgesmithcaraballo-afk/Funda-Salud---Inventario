# filtro antiguo

from config import AZUL_PRIMARIO
import customtkinter as ctk
from components.layout import BaseLayout
import os


class FiltroView(ctk.CTkFrame):
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador

        layout = BaseLayout(self, azul_hex=AZUL_PRIMARIO)
        layout.pack(fill="both", expand=True)

        # Panel izquierdo
        form = layout.left_panel

        # Botón ⬆️ en esquina superior izquierda
        btn_subir = ctk.CTkButton(
            form,
            text="⬆️",
            width=40,
            height=50,
            font=ctk.CTkFont(size=24),
            corner_radius=25,
            fg_color=AZUL_PRIMARIO,
            hover_color="#00367d",
            command=lambda: self.controlador.mostrar_vista("subir"),
        )
        btn_subir.place(relx=0.05, rely=0.05, anchor="nw")

        # Botón 💬 en esquina superior derecha
        btn_chat = ctk.CTkButton(
            form,
            text="💬",
            width=50,
            height=50,
            font=ctk.CTkFont(size=24),
            corner_radius=25,
            fg_color=AZUL_PRIMARIO,
            hover_color="#00367d",
            command=lambda: self.controlador.mostrar_vista("chat"),
        )
        btn_chat.place(relx=0.95, rely=0.05, anchor="ne")

        # Contenido centrado más abajo (para evitar superposición con botones superiores)
        content = ctk.CTkFrame(form, fg_color="transparent")
        content.place(relx=0.5, rely=0.35, anchor="n")

        title = ctk.CTkLabel(
            content, text="FILTRO Y BÚSQUEDA", font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(0, 20))

        filtro_entry = ctk.CTkEntry(
            content, placeholder_text="Buscar...", width=250, font=ctk.CTkFont(size=28)
        )
        filtro_entry.pack()

        # Desplegable estilo select
        self.select_space = ctk.CTkOptionMenu(
            content,
            values=["Space 1", "Space 2", "Space 3"],
            font=ctk.CTkFont(size=22),
            width=250,
            fg_color=AZUL_PRIMARIO,
            button_color=AZUL_PRIMARIO,
        )
        self.select_space.pack(pady=(20, 0))

        # Panel derecho (tabla)
        tabla_contenedor = layout.right_panel

        self.scroll_frame = ctk.CTkScrollableFrame(
            tabla_contenedor, fg_color="white", corner_radius=10
        )
        self.scroll_frame.place(
            relx=0.5, rely=0.5, relwidth=0.9, relheight=0.8, anchor="center"
        )

        # Simular filas
        for i in range(1, 21):
            fila = ctk.CTkLabel(
                self.scroll_frame,
                text=f"Resultado {i}: contenido simulado aquí",
                font=ctk.CTkFont(size=18),
                text_color="#333",
            )
            fila.pack(pady=5, anchor="w", padx=10)
