"""
🤖 Dashboard IA - Sistema de Inventario
UI tipo Dashboard con grid de botones y panel de respuesta
"""

import customtkinter as ctk
import threading
import os
from typing import Optional, Dict, Any
from datetime import datetime
from services.application.chat_ai_service import ChatAIAppService
from models.inventory_models import QueryResult
from resource.colors import (HEADER_BG, HEADER_TEXT, LIGHT_GRAY, VIEW_BACKGROUND, WHITE, 
                   PRIMARY_BLUE, PRIMARY_BLUE_DARK, INPUT_BG, INPUT_BORDER, INPUT_TEXT,
                   BUTTON_SUCCESS_BG, BUTTON_SUCCESS_HOVER, BUTTON_SUCCESS_TEXT,
                   get_header_button_style)
from resource.icons import *

# AI Configuration - read from environment to avoid hardcoding
API_KEY = "AIzaSyBWx-YLBoGowxRBJqO-oenJX3aeZ9J9Zvg"

class ChatAIView(ctk.CTkFrame):
    """Dashboard-style inventory management interface with AI assistance"""
    
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
        self.previous_view = "filtro"
        self._busy = False
        self._query_buttons = []  # hold references to grid buttons to enable/disable
        
        self.configure(fg_color=LIGHT_GRAY)
        
        # Initialize application service (fachada sobre ChatController)
        self._chat_controller = ChatAIAppService(API_KEY)
        self._setup_controller_callbacks()
        
        # Setup dashboard UI
        self._setup_dashboard_ui()
        
        # Always reset to initial state when entering view
        self._reset_to_initial_state()
    
    def _setup_controller_callbacks(self) -> None:
        """Setup callbacks for the chat controller"""
        self._chat_controller.set_query_callbacks(
            on_started=self._on_query_started,
            on_completed=self._on_query_completed,
            on_error=self._on_query_error
        )
    
    def _setup_dashboard_ui(self) -> None:
        """Setup the dashboard-style UI"""
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=HEADER_BG, height=70)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Back button
        back_button_style = get_header_button_style()
        self.back_button = ctk.CTkButton(
            header_content,
            text=ICON_BACK_ARROW,
            command=self.go_back,
            **back_button_style
        )
        self.back_button.pack(side="left", anchor="w")
        
        # Title
        title_label = ctk.CTkLabel(
            header_content,
            text="🤖 Asistente IA - Inventario",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=HEADER_TEXT
        )
        title_label.pack(side="left", expand=True, padx=(20, 0))
        
        # AI status
        status_text = "🟢 IA Activa" if self._chat_controller.is_ai_configured() else "🟡 IA Básica"
        status_label = ctk.CTkLabel(
            header_content,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color=HEADER_TEXT
        )
        status_label.pack(side="right")
        
        # Grid Panel (Questions + Search)
        self._setup_grid_panel()
        
        # Response Panel
        self._setup_response_panel()
    
    def _setup_grid_panel(self) -> None:
        """Setup the grid panel with question buttons and search"""
        
        # Grid container
        grid_frame = ctk.CTkFrame(self, fg_color=WHITE)
        grid_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Title
        grid_title = ctk.CTkLabel(
            grid_frame,
            text="📋 Selecciona una consulta:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PRIMARY_BLUE
        )
        grid_title.pack(pady=(15, 10))
        
        # Buttons container
        buttons_container = ctk.CTkFrame(grid_frame, fg_color="transparent")
        buttons_container.pack(pady=(0, 10), padx=20, fill="x")
        
        # Get available queries
        available_queries = self._chat_controller.get_available_queries()
        
        # Create grid of buttons (3 columns)
        button_order = [
            "stock_bajo", "sin_stock", "valor_inventario",
            "mas_entradas", "mas_salidas", "monto_entradas", 
            "monto_salidas", "sin_movimiento", "variacion_stock"
        ]
        
        for i, query_key in enumerate(button_order):
            if query_key in available_queries:
                query_info = available_queries[query_key]
                self._create_grid_button(buttons_container, query_key, query_info, i)
        
        # Free search section
        self._setup_search_section(grid_frame)
    
    def _create_grid_button(self, parent, query_key: str, query_info: Dict[str, Any], index: int) -> None:
        """Create a grid button for query"""
        
        row = index // 3
        col = index % 3
        
        btn = ctk.CTkButton(
            parent,
            text=query_info['title'],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=50,
            width=200,
            fg_color=query_info['color'],
            hover_color=self._darken_color(query_info['color']),
            command=lambda key=query_key: self._handle_question_click(key),
            corner_radius=8,
            text_color="white"
        )
        btn.grid(row=row, column=col, padx=8, pady=6, sticky="ew")
        # track button for enable/disable
        try:
            self._query_buttons.append(btn)
        except Exception:
            pass
        
        # Configure column weights for responsive design
        parent.grid_columnconfigure(col, weight=1)
    
    def _setup_search_section(self, parent) -> None:
        """Setup the free search section"""
        
        # Search container
        search_frame = ctk.CTkFrame(parent, fg_color=LIGHT_GRAY, corner_radius=8)
        search_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        # Search title
        search_title = ctk.CTkLabel(
            search_frame,
            text="🔍 Búsqueda Libre (por ID o descripción):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=PRIMARY_BLUE
        )
        search_title.pack(pady=(10, 5))
        
        # Search input container
        input_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_container.pack(pady=(0, 10), padx=15, fill="x")
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="ID (ej: 5) o descripción (ej: Jeringa)",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=INPUT_TEXT
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Search button
        self.search_button = ctk.CTkButton(
            input_container,
            text="🔍 Buscar",
            width=100,
            height=40,
            command=self._handle_search_click,
            fg_color=BUTTON_SUCCESS_BG,
            hover_color=BUTTON_SUCCESS_HOVER,
            text_color=BUTTON_SUCCESS_TEXT,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.search_button.pack(side="right")
        
        # Bind Enter key
        self.search_entry.bind("<Return>", lambda e: self._handle_search_click())
    
    def _setup_response_panel(self) -> None:
        """Setup the response panel"""
        
        # Response container
        response_frame = ctk.CTkFrame(self, fg_color=WHITE)
        response_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Response title
        response_title = ctk.CTkLabel(
            response_frame,
            text="📋 Respuesta:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PRIMARY_BLUE
        )
        response_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Response text area (scrollable and expandable)
        self.response_text = ctk.CTkTextbox(
            response_frame,
            height=350,
            font=ctk.CTkFont(size=13),
            fg_color=LIGHT_GRAY,
            text_color=PRIMARY_BLUE_DARK,
            border_width=1,
            border_color=INPUT_BORDER,
            corner_radius=8,
            wrap="word",
            scrollbar_button_color=PRIMARY_BLUE,
            scrollbar_button_hover_color=PRIMARY_BLUE_DARK
        )
        self.response_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Set initial message
        self._set_initial_message()
    
    def _reset_to_initial_state(self) -> None:
        """Reset dashboard to clean initial state"""
        # Clear search field and ensure placeholder shows
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, 'end')
            # Force focus away to ensure placeholder shows
            self.focus_set()
        
        # Reset to initial message
        self._set_initial_message()
    
    def _set_initial_message(self) -> None:
        """Set initial welcome message with clean formatting"""
        initial_message = """¡Bienvenido al Asistente IA de Inventario! 👋

📊 ¿Qué puedes hacer aquí?

• 9 Consultas Predefinidas: Haz clic en cualquier botón de color para obtener información específica sobre tu inventario

• Búsqueda Libre: Busca un producto específico por ID o descripción

🤖 IA Inteligente: Las respuestas incluyen:
• Resumen de resultados
• Lista de productos relevantes  
• Recomendaciones automáticas

💡 Tip: ¡Comienza haciendo clic en cualquier consulta que te interese!"""
        
        self.response_text.configure(state="normal")
        self.response_text.delete("0.0", "end")
        self.response_text.insert("0.0", initial_message)
        self.response_text.configure(state="disabled")
    
    def _handle_question_click(self, query_key: str) -> None:
        """Handle when a question button is clicked"""
        if self._busy:
            return
        self._busy = True
        self._set_controls_enabled(False)
        self._show_loading_message(f"🤔 Analizando {query_key.replace('_', ' ').title()}...")
        self._chat_controller.execute_query_async(query_key)
    
    def _handle_search_click(self) -> None:
        """Handle search button click"""
        if self._busy:
            return
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self._show_error_message("❌ Por favor, ingresa un ID o descripción de producto")
            return
        
        self._busy = True
        self._set_controls_enabled(False)
        self._show_loading_message(f"🔍 Buscando: '{search_term}'...")
        self._chat_controller.search_product_async(search_term)
        
        # Clear search field
        self.search_entry.delete(0, 'end')
    
    def _show_loading_message(self, message: str) -> None:
        """Show loading message in response panel"""
        self.response_text.configure(state="normal")
        self.response_text.delete("0.0", "end")
        self.response_text.insert("0.0", f"{message}\n\n⏳ Por favor espera...")
        self.response_text.configure(state="disabled")
    
    def _show_error_message(self, message: str) -> None:
        """Show error message in response panel"""
        self.response_text.configure(state="normal")
        self.response_text.delete("0.0", "end")
        self.response_text.insert("0.0", f"{message}\n\n💡 Intenta con otra consulta.")
        self.response_text.configure(state="disabled")
    
    def _show_response_message(self, message: str) -> None:
        """Show response message in response panel"""
        self.response_text.configure(state="normal")
        self.response_text.delete("0.0", "end")
        self.response_text.insert("0.0", message)
        self.response_text.configure(state="disabled")
    
    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Darken a hex color by a factor"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            darkened_rgb = tuple(int(c * factor) for c in rgb)
            return '#{:02x}{:02x}{:02x}'.format(*darkened_rgb)
        except:
            return "#666666"
    
    # Chat controller callbacks
    def _on_query_started(self) -> None:
        """Called when a query starts processing"""
        pass  # Loading message already shown
    
    def _on_query_completed(self, result: QueryResult) -> None:
        """Called when a query completes successfully"""
        def _done():
            self._display_query_result(result)
            self._busy = False
            self._set_controls_enabled(True)
        self.after(0, _done)
    
    def _on_query_error(self, error_message: str) -> None:
        """Called when a query fails"""
        def _done():
            self._show_error_message(error_message)
            self._busy = False
            self._set_controls_enabled(True)
        self.after(0, _done)

    def _set_controls_enabled(self, enabled: bool) -> None:
        try:
            state = "normal" if enabled else "disabled"
            # search
            if hasattr(self, 'search_button'):
                self.search_button.configure(state=state)
            if hasattr(self, 'search_entry'):
                self.search_entry.configure(state=state)
            # query buttons
            for b in getattr(self, '_query_buttons', []) or []:
                b.configure(state=state)
        except Exception:
            pass
    
    def _display_query_result(self, result: QueryResult) -> None:
        """Display the query result in the response panel"""
        
        if result.ai_response:
            response_text = result.ai_response
        else:
            response_text = f"📊 Consulta completada.\n\nSe encontraron {len(result.data)} registros."
        
        self._show_response_message(response_text)
    
    def set_previous_view(self, view_name):
        """Set the previous view for navigation"""
        self.previous_view = view_name
    
    def reset_view_state(self):
        """Public method to reset view state when entering"""
        self._reset_to_initial_state()
    
    def go_back(self):
        """Return to previous view"""
        try:
            self.controlador.mostrar_vista(self.previous_view)
        except Exception as e:
            print(f"❌ Error de navegación: {e}")
            self.controlador.mostrar_vista("filtro")
    
    def cleanup(self):
        """Handle cleanup when switching views"""
        try:
            if hasattr(self, '_chat_controller'):
                pass
        except Exception as e:
            print(f"Error during cleanup: {e}")


if __name__ == "__main__":
    print("ChatAIView es una vista integrada, no puede ejecutarse independientemente.")
    print("Para probar, ejecuta main.py")
