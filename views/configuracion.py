import customtkinter as ctk
from colors import (VIEW_BACKGROUND, HEADER_BG, HEADER_TEXT, LIGHT_GRAY, 
                   TEXT_PRIMARY, TEXT_SECONDARY, get_header_button_style)
from icons import *
from strings import CONFIG_TITLE
from typing import Any


class ConfiguracionView(ctk.CTkFrame):
    def __init__(self, master: Any, controlador: Any):
        super().__init__(master)
        self.controlador = controlador
        self.previous_view = "filtro"  # Default previous view
        
        # Main background
        self.configure(fg_color=VIEW_BACKGROUND)
        
        # Header with back button
        header_frame = ctk.CTkFrame(self, fg_color=HEADER_BG, height=70)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Back button (left)
        back_button_style = get_header_button_style()
        self.back_button = ctk.CTkButton(
            header_content,
            text=ICON_BACK_ARROW,
            command=self.go_back,
            **back_button_style
        )
        self.back_button.pack(side="left", anchor="w")
        
        # Title (center)
        title_label = ctk.CTkLabel(
            header_content,
            text=f"{ICON_SETTINGS} {CONFIG_TITLE}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=HEADER_TEXT
        )
        title_label.pack(side="left", expand=True, padx=(20, 0))
        
        # Spacer for balance
        spacer = ctk.CTkFrame(header_content, width=45, height=45, fg_color="transparent")
        spacer.pack(side="right", anchor="e")
        
        # Main content area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configuration options placeholder
        config_label = ctk.CTkLabel(
            content_frame,
            text="⚙️ Configuración del Sistema",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        config_label.pack(pady=(20, 40))
        
        # Add some configuration options
        options_frame = ctk.CTkFrame(content_frame, fg_color=LIGHT_GRAY, corner_radius=10)
        options_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Placeholder content
        placeholder_label = ctk.CTkLabel(
            options_frame,
            text="🚧 Configuraciones disponibles próximamente...",
            font=ctk.CTkFont(size=16),
            text_color=TEXT_SECONDARY
        )
        placeholder_label.pack(pady=50)
    
    def set_previous_view(self, view_name: str) -> None:
        """Set the previous view for navigation"""
        self.previous_view = view_name
    
    def go_back(self) -> None:
        """Go back to previous view"""
        try:
            print(f"🔙 Regresando a vista: {self.previous_view}")
            self.controlador.mostrar_vista(self.previous_view)
        except Exception as e:
            print(f"❌ Error regresando a vista anterior: {e}")
            # Fallback to filtro
            self.controlador.mostrar_vista("filtro")
