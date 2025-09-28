"""
🤖 Dashboard IA - Sistema de Inventario
UI tipo Dashboard con grid de botones y panel de respuesta
"""

import customtkinter as ctk
import threading
from typing import Optional, Dict, Any
from services.application.chat_ai_service import ChatAIAppService
from models.inventory_models import QueryResult
from resource.colors import (
    LIGHT_GRAY,
    WHITE,
    PRIMARY_BLUE,
    PRIMARY_BLUE_DARK,
    GRAY,
    TEXT_PRIMARY,
    SUCCESS_GREEN,
    SUCCESS_GREEN_HOVER,
    TEXT_MUTED,
)
from resource.sizes import (
    HEADER_HEIGHT,
    GRID_BUTTON_HEIGHT,
    GRID_BUTTON_WIDTH,
    SEARCH_BUTTON_WIDTH,
    SEARCH_HEIGHT,
    SEARCH_ENTRY_HEIGHT,
    RESPONSE_TEXT_HEIGHT,
)
from resource.fonts import (
    FONT_SM,
    FONT_MD,
    FONT_LG,
    FONT_XL,
    WEIGHT_BOLD,
    WEIGHT_NORMAL,
)
from resource.spacing import (
    PADDING_MD,
    PADDING_LG,
    PADDING_XL,
    GAP_MD,
    RADIUS_MD,
)
from resource.strings import (
    CHAT_TITLE,
    CHAT_STATUS_ACTIVE,
    CHAT_STATUS_BASIC,
    SELECCIONA_UNA_CONSULTA,
    RESPUESTA,
)
from views.toolbar import Toolbar

# AI Configuration - local hardcoded API key (consider env variables in production)
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
        # Root grid layout (header, status, grid panel, response panel)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

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
            on_error=self._on_query_error,
        )

    def _setup_dashboard_ui(self) -> None:
        """Setup the dashboard-style UI"""

        # Header (Toolbar reutilizable)
        toolbar = Toolbar(
            self,
            title=CHAT_TITLE,
            on_go_subir=self.go_back,
            on_go_chat=None,
            on_go_config=None,
        )
        toolbar.grid(row=0, column=0, sticky="ew")
        try:
            toolbar.configure_buttons(show_chat=False, show_config=False)
        except Exception:
            pass
        # Optional: show AI status below toolbar
        status_text = (
            CHAT_STATUS_ACTIVE
            if self._chat_controller.is_ai_configured()
            else CHAT_STATUS_BASIC
        )
        status_label = ctk.CTkLabel(
            self,
            text=status_text,
            font=ctk.CTkFont(size=FONT_SM),
            text_color=PRIMARY_BLUE,
        )
        status_label.grid(row=1, column=0, sticky="e", padx=PADDING_XL, pady=(0, 4))

        # Grid Panel (Questions + Search)
        self._setup_grid_panel()

        # Response Panel
        self._setup_response_panel()

    def _setup_grid_panel(self) -> None:
        """Setup the grid panel with question buttons and search"""

        # Grid container
        grid_frame = ctk.CTkFrame(self, fg_color=WHITE)
        grid_frame.grid(
            row=2, column=0, sticky="ew", padx=PADDING_MD, pady=(PADDING_MD, 5)
        )

        # Title
        grid_title = ctk.CTkLabel(
            grid_frame,
            text=SELECCIONA_UNA_CONSULTA,
            font=ctk.CTkFont(size=FONT_LG, weight=WEIGHT_BOLD),
            text_color=PRIMARY_BLUE,
        )
        grid_title.pack(pady=(15, 10))

        # Buttons container
        buttons_container = ctk.CTkFrame(grid_frame, fg_color="transparent")
        buttons_container.pack(pady=(0, PADDING_MD), padx=PADDING_XL, fill="x")

        # Get available queries
        available_queries = self._chat_controller.get_available_queries()

        # Create grid of buttons (3 columns)
        button_order = [
            "stock_bajo",
            "sin_stock",
            "valor_inventario",
            "mas_entradas",
            "mas_salidas",
            "monto_entradas",
            "monto_salidas",
            "sin_movimiento",
            "variacion_stock",
        ]

        for i, query_key in enumerate(button_order):
            if query_key in available_queries:
                query_info = available_queries[query_key]
                self._create_grid_button(buttons_container, query_key, query_info, i)

        # Free search section
        self._setup_search_section(grid_frame)

    def _create_grid_button(
        self, parent, query_key: str, query_info: Dict[str, Any], index: int
    ) -> None:
        """Create a grid button for query"""

        row = index // 3
        col = index % 3

        btn = ctk.CTkButton(
            parent,
            text=query_info["title"],
            font=ctk.CTkFont(size=FONT_SM, weight=WEIGHT_BOLD),
            height=GRID_BUTTON_HEIGHT,
            width=GRID_BUTTON_WIDTH,
            fg_color=query_info["color"],
            hover_color=self._darken_color(query_info["color"]),
            command=lambda key=query_key: self._handle_question_click(key),
            corner_radius=RADIUS_MD,
            text_color="white",
        )
        btn.grid(row=row, column=col, padx=GAP_MD, pady=GAP_MD, sticky="ew")
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
        search_frame = ctk.CTkFrame(
            parent, fg_color=LIGHT_GRAY, corner_radius=RADIUS_MD
        )
        search_frame.pack(fill="x", padx=PADDING_XL, pady=(PADDING_MD, PADDING_LG))

        # Search title
        search_title = ctk.CTkLabel(
            search_frame,
            text="🔍 Búsqueda Libre (por Código o descripción):",
            font=ctk.CTkFont(size=FONT_MD, weight=WEIGHT_BOLD),
            text_color=PRIMARY_BLUE,
        )
        search_title.pack(pady=(10, 5))

        # Search input container
        input_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_container.pack(pady=(0, PADDING_MD), padx=PADDING_LG, fill="x")

        # Search entry
        self.search_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Código (ej: 5) o descripción (ej: Jeringa)",
            font=ctk.CTkFont(size=FONT_MD),
            height=SEARCH_ENTRY_HEIGHT,
            fg_color=WHITE,
            border_color=GRAY,
            text_color=TEXT_PRIMARY,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Search button
        self.search_button = ctk.CTkButton(
            input_container,
            text="🔍 Buscar",
            width=SEARCH_BUTTON_WIDTH,
            height=SEARCH_HEIGHT,
            command=self._handle_search_click,
            fg_color=SUCCESS_GREEN,
            hover_color=SUCCESS_GREEN_HOVER,
            text_color="white",
            font=ctk.CTkFont(size=FONT_SM, weight=WEIGHT_BOLD),
        )
        self.search_button.pack(side="right")

        # Bind Enter key
        self.search_entry.bind("<Return>", lambda e: self._handle_search_click())

    def _setup_response_panel(self) -> None:
        """Setup the response panel"""

        # Response container
        response_frame = ctk.CTkFrame(self, fg_color=WHITE)
        response_frame.grid(
            row=3, column=0, sticky="nsew", padx=PADDING_MD, pady=(5, PADDING_MD)
        )

        # Response title
        response_title = ctk.CTkLabel(
            response_frame,
            text=RESPUESTA,
            font=ctk.CTkFont(size=FONT_LG, weight=WEIGHT_BOLD),
            text_color=PRIMARY_BLUE,
        )
        response_title.pack(anchor="w", padx=20, pady=(15, 10))

        # Response text area (scrollable and expandable)
        self.response_text = ctk.CTkTextbox(
            response_frame,
            height=RESPONSE_TEXT_HEIGHT,
            font=ctk.CTkFont(size=FONT_MD),
            fg_color=LIGHT_GRAY,
            text_color=PRIMARY_BLUE_DARK,
            border_width=1,
            border_color=GRAY,
            corner_radius=RADIUS_MD,
            wrap="word",
            scrollbar_button_color=PRIMARY_BLUE,
            scrollbar_button_hover_color=PRIMARY_BLUE_DARK,
        )
        self.response_text.pack(
            fill="both", expand=True, padx=PADDING_XL, pady=(0, PADDING_XL)
        )

        # Set initial message
        self._set_initial_message()

    def _reset_to_initial_state(self) -> None:
        """Reset dashboard to clean initial state"""
        # Clear search field and ensure placeholder shows
        if hasattr(self, "search_entry"):
            self.search_entry.delete(0, "end")
            # Force focus away to ensure placeholder shows
            self.focus_set()

        # Reset to initial message
        self._set_initial_message()

    def _set_initial_message(self) -> None:
        """Set initial welcome message with clean formatting"""
        initial_message = """¡Bienvenido al Asistente IA de Inventario! 👋

📊 ¿Qué puedes hacer aquí?

• 9 Consultas Predefinidas: Haz clic en cualquier botón de color para obtener información específica sobre tu inventario

• Búsqueda Libre: Busca un producto específico por Código o descripción

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
        self._show_loading_message(
            f"🤔 Analizando {query_key.replace('_', ' ').title()}..."
        )
        self._chat_controller.execute_query_async(query_key)

    def _handle_search_click(self) -> None:
        """Handle search button click"""
        if self._busy:
            return
        search_term = self.search_entry.get().strip()

        if not search_term:
            self._show_error_message(
                "❌ Por favor, ingresa un Código o descripción de producto"
            )
            return

        self._busy = True
        self._set_controls_enabled(False)
        self._show_loading_message(f"🔍 Buscando: '{search_term}'...")
        self._chat_controller.search_product_async(search_term)

        # Clear search field
        self.search_entry.delete(0, "end")

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
            hex_color = hex_color.lstrip("#")
            rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            darkened_rgb = tuple(int(c * factor) for c in rgb)
            return "#{:02x}{:02x}{:02x}".format(*darkened_rgb)
        except:
            return TEXT_MUTED

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
            if hasattr(self, "search_button"):
                self.search_button.configure(state=state)
            if hasattr(self, "search_entry"):
                self.search_entry.configure(state=state)
            # query buttons
            for b in getattr(self, "_query_buttons", []) or []:
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
            if hasattr(self, "_chat_controller"):
                pass
        except Exception as e:
            print(f"Error during cleanup: {e}")


if __name__ == "__main__":
    print("ChatAIView es una vista integrada, no puede ejecutarse independientemente.")
    print("Para probar, ejecuta main.py")
