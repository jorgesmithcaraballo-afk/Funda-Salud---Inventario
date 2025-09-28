"""
Simple Database Error View
Displays connection error message with retry option
"""

import customtkinter as ctk
from resource.colors import (
    PRIMARY_BLUE,
    WHITE,
    ERROR_RED,
    ERROR_RED_BG,
    SECONDARY_BLUE,
    SECONDARY_BLUE_HOVER,
    get_content_button_style,
)
from resource.strings import (
    DB_ERROR_TITLE,
    DB_ERROR_MAIN_MESSAGE,
    DB_ERROR_BUTTON_RETRY,
)
from PIL import Image
import os

LOGO_PATH = os.path.join("img", "logo.png")


class DatabaseErrorView(ctk.CTkFrame):
    """Simple error view for database connection issues"""

    def __init__(self, master, controlador, error_message="Connection failed"):
        super().__init__(master)
        self.controlador = controlador
        self.error_message = error_message

        # Main background
        self.configure(fg_color=WHITE)

        # Main content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Error icon and title
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.pack(pady=(0, 30))

        title_label = ctk.CTkLabel(
            title_frame,
            text=DB_ERROR_TITLE,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=ERROR_RED,
        )
        title_label.pack()

        # Error message
        message_frame = ctk.CTkFrame(
            content_frame, fg_color=ERROR_RED_BG, corner_radius=10
        )
        message_frame.pack(fill="x", pady=(0, 30))

        message_label = ctk.CTkLabel(
            message_frame,
            text=f"{DB_ERROR_MAIN_MESSAGE}\n\nError: {self.error_message}",
            font=ctk.CTkFont(size=16),
            text_color=ERROR_RED,
            justify="center",
        )
        message_label.pack(pady=20, padx=20)

        # Retry button (use unified content button size, keep primary colors)
        _btn_style = get_content_button_style()
        _btn_style = {
            **_btn_style,
            "fg_color": SECONDARY_BLUE,
            "hover_color": SECONDARY_BLUE_HOVER,
            "text_color": WHITE,
            "font": ctk.CTkFont(size=18, weight="bold"),
        }
        retry_button = ctk.CTkButton(
            content_frame,
            text=DB_ERROR_BUTTON_RETRY,
            command=self.retry_connection,
            **_btn_style,
        )
        retry_button.pack(pady=10)

        # Logo (optional)
        try:
            if os.path.exists(LOGO_PATH):
                logo_image = ctk.CTkImage(Image.open(LOGO_PATH), size=(150, 150))
                logo_label = ctk.CTkLabel(content_frame, image=logo_image, text="")
                logo_label.pack(pady=30)
        except Exception:
            # If logo fails to load, show text logo
            logo_label = ctk.CTkLabel(
                content_frame,
                text="Sistema de Inventario\nFundación Salud",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=PRIMARY_BLUE,
                justify="center",
            )
            logo_label.pack(pady=30)

    def retry_connection(self):
        """Retry database connection"""
        try:
            # Try to reconnect
            from conexion import obtener_conexion

            conn = obtener_conexion()
            conn.close()

            # If successful, go to login
            self.controlador.mostrar_vista("login")

        except Exception as e:
            # Update error message and stay in error view
            self.error_message = str(e)
            # Could update the message label here, but keeping it simple for now
            print(f"❌ Retry failed: {e}")
