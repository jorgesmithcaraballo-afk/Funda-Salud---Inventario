"""
🤖 Dashboard IA - Sistema de Inventario
UI tipo Dashboard con grid de botones y panel de respuesta
"""

import customtkinter as ctk
import threading
from typing import Optional, Dict, Any
from datetime import datetime
from controllers.chat_controller import ChatController
from models.inventory_models import QueryResult
from colors import (HEADER_BG, HEADER_TEXT, LIGHT_GRAY, VIEW_BACKGROUND, WHITE, 
                   PRIMARY_BLUE, PRIMARY_BLUE_DARK, INPUT_BG, INPUT_BORDER, INPUT_TEXT,
                   BUTTON_SUCCESS_BG, BUTTON_SUCCESS_HOVER, BUTTON_SUCCESS_TEXT,
                   get_header_button_style)
from icons import *

# AI Configuration - PUT YOUR GEMINI API KEY HERE
API_KEY = "AIzaSyBWx-YLBoGowxRBJqO-oenJX3aeZ9J9Zvg"

class ChatAIView(ctk.CTkFrame):
<<<<<<< HEAD
    """Dashboard-style inventory management interface with AI assistance"""
=======
    """Main WhatsApp-style chat application for inventory management"""
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
    
    def __init__(self, master, controlador):
        super().__init__(master)
        self.controlador = controlador
<<<<<<< HEAD
        self.previous_view = "filtro"
        
        self.configure(fg_color=LIGHT_GRAY)
=======
        self.previous_view = "filtro"  # Vista anterior por defecto
        
        # Frame configuration using unified colors
        self.configure(fg_color=LIGHT_GRAY)
        
        # Chat state - simplified without product-specific mode
        self.current_mode = "general"  # Always general mode
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
        
        # Initialize controller
        self._chat_controller = ChatController(API_KEY)
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
        
<<<<<<< HEAD
        # Header
=======
        # Header unificado con botón de regreso
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
        header_frame = ctk.CTkFrame(self, fg_color=HEADER_BG, height=70)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20, pady=15)
        
<<<<<<< HEAD
        # Back button
=======
        # Botón de flecha atrás (izquierda)
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
        back_button_style = get_header_button_style()
        self.back_button = ctk.CTkButton(
            header_content,
            text=ICON_BACK_ARROW,
            command=self.go_back,
            **back_button_style
        )
        self.back_button.pack(side="left", anchor="w")
        
<<<<<<< HEAD
        # Title
=======
        # Título centrado
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
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
        
<<<<<<< HEAD
        # Grid container
        grid_frame = ctk.CTkFrame(self, fg_color=WHITE)
        grid_frame.pack(fill="x", padx=10, pady=(10, 5))
=======
        # Chat Container con colores unificados
        chat_container = ctk.CTkFrame(self, fg_color=WHITE)
        chat_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollable Chat Frame
        self.chat_scrollable = ctk.CTkScrollableFrame(
            chat_container,
            fg_color=WHITE,
            scrollbar_button_color=PRIMARY_BLUE,
            scrollbar_button_hover_color=PRIMARY_BLUE_DARK
        )
        self.chat_scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure scrollable frame
        self.chat_scrollable.configure(corner_radius=0)
        
        # Enable mouse wheel scrolling
        self._setup_mouse_wheel_scrolling()
        
        # Additional CustomTkinter specific setup
        self._setup_customtkinter_scroll()
    
    def _setup_input_area(self) -> None:
        """Setup the input area (hidden by default)"""
        
        self.input_frame = ctk.CTkFrame(self, fg_color=LIGHT_GRAY, height=80)
        self.input_frame.pack(fill="x", padx=10, pady=10)
        self.input_frame.pack_forget()  # Hide initially
        self.input_frame.pack_propagate(False)
        
        # Input container
        input_container = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        input_container.pack(expand=True, fill="both", padx=15, pady=15)
        
        # Text entry
        self.text_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Escribe el nombre del producto...",
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color=INPUT_BG,
            border_color=INPUT_BORDER,
            text_color=INPUT_TEXT
        )
        self.text_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Send button con colores unificados
        self.send_button = ctk.CTkButton(
            input_container,
            text="Enviar 📤",
            width=100,
            height=40,
            command=self._send_text_message,
            fg_color=BUTTON_SUCCESS_BG,
            hover_color=BUTTON_SUCCESS_HOVER,
            text_color=BUTTON_SUCCESS_TEXT
        )
        self.send_button.pack(side="right")
        
        # Bind Enter key
        self.text_entry.bind("<Return>", lambda e: self._send_text_message())
    
    def _setup_mouse_wheel_scrolling(self) -> None:
        """Setup mouse wheel scrolling AND click-drag scrolling for the chat area"""
        
        # Variables for click and drag scrolling
        self._drag_start_y = 0
        self._is_dragging = False
        
        def on_mouse_wheel(event):
            """Handle mouse wheel scrolling in chat area"""
            try:
                # Get the canvas from the scrollable frame
                if hasattr(self.chat_scrollable, '_parent_canvas'):
                    canvas = self.chat_scrollable._parent_canvas
                    
                    # Calculate scroll amount
                    if hasattr(event, 'delta'):
                        # Windows and macOS
                        delta = event.delta
                    else:
                        # Linux - Button-4 is up, Button-5 is down
                        if event.num == 4:
                            delta = 120
                        elif event.num == 5:
                            delta = -120
                        else:
                            return
                    
                    # Scroll the canvas
                    canvas.yview_scroll(int(-delta/120), "units")
                    return "break"  # Prevent further event processing
                    
            except Exception as e:
                print(f"Scroll error: {e}")
        
        def on_button_press(event):
            """Handle mouse button press for drag scrolling"""
            if event.num == 1:  # Left mouse button
                self._drag_start_y = event.y
                self._is_dragging = True
                return "break"
        
        def on_button_release(event):
            """Handle mouse button release"""
            if event.num == 1:  # Left mouse button
                self._is_dragging = False
                return "break"
        
        def on_mouse_motion(event):
            """Handle mouse motion for drag scrolling"""
            if self._is_dragging:
                try:
                    if hasattr(self.chat_scrollable, '_parent_canvas'):
                        canvas = self.chat_scrollable._parent_canvas
                        
                        # Calculate the difference in Y position
                        delta_y = event.y - self._drag_start_y
                        
                        # Convert pixel movement to scroll units (adjust sensitivity)
                        scroll_units = int(-delta_y / 10)  # Adjust 10 for sensitivity
                        
                        if scroll_units != 0:
                            canvas.yview_scroll(scroll_units, "units")
                            self._drag_start_y = event.y  # Update start position
                        
                        return "break"
                except Exception as e:
                    print(f"Drag scroll error: {e}")
        
        # Bind mouse wheel events
        # Bind scroll events only to this frame (not globally)
        try:
            self.bind("<MouseWheel>", on_mouse_wheel)
            if hasattr(self, 'chat_container'):
                self.chat_container.bind("<MouseWheel>", on_mouse_wheel)
        except Exception as e:
            print(f"Warning: Could not bind scroll events: {e}")
        
        # Touch/drag simulation disabled in Frame mode
        
        # Also bind to the scrollable frame
        try:
            self.chat_scrollable.bind("<MouseWheel>", on_mouse_wheel)
            self.chat_scrollable.bind("<Button-4>", on_mouse_wheel) 
            self.chat_scrollable.bind("<Button-5>", on_mouse_wheel)
            
            # Click and drag on scrollable frame
            self.chat_scrollable.bind("<Button-1>", on_button_press)
            self.chat_scrollable.bind("<ButtonRelease-1>", on_button_release)
            self.chat_scrollable.bind("<B1-Motion>", on_mouse_motion)
        except:
            pass
            
        # Make sure the scrollable frame can receive focus
        try:
            self.chat_scrollable.focus_set()
            self.update()  # Force update to ensure bindings are active
        except:
            pass
    
    def _bind_scroll_to_widget(self, widget) -> None:
        """Bind mouse wheel scrolling to a specific widget - simplified"""
        # This is now handled by the global binding, so we can simplify or remove this
        pass
    
    def _setup_customtkinter_scroll(self) -> None:
        """Additional CustomTkinter specific scroll setup"""
        
        def handle_scroll(event):
            """More specific scroll handler for CustomTkinter"""
            try:
                # Try different approaches to get the scrollable area
                if hasattr(self.chat_scrollable, '_scrollbar'):
                    # Try using the scrollbar directly
                    scrollbar = self.chat_scrollable._scrollbar
                    if scrollbar and hasattr(scrollbar, 'delta'):
                        scrollbar.delta(-1 if event.delta > 0 else 1)
                        
                elif hasattr(self.chat_scrollable, '_parent_canvas'):
                    # Use the parent canvas approach
                    canvas = self.chat_scrollable._parent_canvas
                    canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
                    
                return "break"
            except:
                pass
        
        # Try to bind mouse events more directly
        try:
            # Get the actual frame widget
            if hasattr(self.chat_scrollable, 'winfo_children'):
                for child in self.chat_scrollable.winfo_children():
                    try:
                        child.bind("<MouseWheel>", handle_scroll)
                        child.bind("<Button-4>", lambda e: handle_scroll(type('Event', (), {'delta': 120})()))
                        child.bind("<Button-5>", lambda e: handle_scroll(type('Event', (), {'delta': -120})()))
                    except:
                        continue
                        
            # Also try binding to the container itself
            chat_container = self.chat_scrollable.master
            if chat_container:
                chat_container.bind("<MouseWheel>", handle_scroll)
                chat_container.bind("<Button-4>", lambda e: handle_scroll(type('Event', (), {'delta': 120})()))
                chat_container.bind("<Button-5>", lambda e: handle_scroll(type('Event', (), {'delta': -120})()))
                
        except Exception as e:
            print(f"CustomTkinter scroll setup error: {e}")
    
    def _ensure_scroll_working(self) -> None:
        """Final attempt to ensure mouse wheel and drag scrolling works"""
        
        def universal_scroll_handler(event):
            """Universal scroll handler that tries multiple approaches"""
            # Calculate delta
            if hasattr(event, 'delta'):
                delta = event.delta
            elif hasattr(event, 'num'):
                delta = 120 if event.num == 4 else -120 if event.num == 5 else 0
            else:
                return
            
            # Try scrolling
            try:
                if hasattr(self.chat_scrollable, '_parent_canvas'):
                    canvas = self.chat_scrollable._parent_canvas
                    scroll_amount = -1 if delta > 0 else 1
                    canvas.yview_scroll(scroll_amount, "units")
                    return "break"
            except:
                pass
        
        def universal_drag_start(event):
            if event.num == 1:
                self._drag_start_y = event.y
                self._is_dragging = True
                return "break"
        
        def universal_drag_end(event):
            if event.num == 1:
                self._is_dragging = False
                return "break"
        
        def universal_drag_motion(event):
            if self._is_dragging:
                try:
                    if hasattr(self.chat_scrollable, '_parent_canvas'):
                        canvas = self.chat_scrollable._parent_canvas
                        delta_y = event.y - self._drag_start_y
                        scroll_units = int(-delta_y / 10)
                        
                        if scroll_units != 0:
                            canvas.yview_scroll(scroll_units, "units")
                            self._drag_start_y = event.y
                        
                        return "break"
                except:
                    pass
        
        # Bind to every possible element
        try:
            # Main window - wheel scroll
            self.bind("<MouseWheel>", universal_scroll_handler, "+")
            self.bind("<Button-4>", universal_scroll_handler, "+")
            self.bind("<Button-5>", universal_scroll_handler, "+")
            
            # Main window - drag scroll (disabled to avoid interfering with buttons)
            # self.bind("<Button-1>", universal_drag_start, "+")
            # self.bind("<ButtonRelease-1>", universal_drag_end, "+")
            # self.bind("<B1-Motion>", universal_drag_motion, "+")
            
            # Chat scrollable and its children - wheel scroll
            self.chat_scrollable.bind("<MouseWheel>", universal_scroll_handler, "+")
            self.chat_scrollable.bind("<Button-4>", universal_scroll_handler, "+")
            self.chat_scrollable.bind("<Button-5>", universal_scroll_handler, "+")
            
            # Chat scrollable and its children - drag scroll
            self.chat_scrollable.bind("<Button-1>", universal_drag_start, "+")
            self.chat_scrollable.bind("<ButtonRelease-1>", universal_drag_end, "+")
            self.chat_scrollable.bind("<B1-Motion>", universal_drag_motion, "+")
            
            # All existing children
            for widget in self.chat_scrollable.winfo_children():
                try:
                    # Wheel scroll for all widgets
                    widget.bind("<MouseWheel>", universal_scroll_handler, "+")
                    widget.bind("<Button-4>", universal_scroll_handler, "+")
                    widget.bind("<Button-5>", universal_scroll_handler, "+")
                    
                    # Drag scroll ONLY for non-button widgets
                    widget_class = widget.winfo_class()
                    if widget_class not in ["Button", "CTkButton"]:
                        widget.bind("<Button-1>", universal_drag_start, "+")
                        widget.bind("<ButtonRelease-1>", universal_drag_end, "+")
                        widget.bind("<B1-Motion>", universal_drag_motion, "+")
                except:
                    pass
                    
            print("✅ Scroll and drag bindings applied successfully")
            
        except Exception as e:
            print(f"Error setting up scroll and drag: {e}")
    
    def _apply_scroll_to_element(self, element) -> None:
        """Apply scroll functionality (wheel + drag) to a new element"""
        def element_scroll(event):
            try:
                if hasattr(self.chat_scrollable, '_parent_canvas'):
                    canvas = self.chat_scrollable._parent_canvas
                    delta = event.delta if hasattr(event, 'delta') else (120 if event.num == 4 else -120 if event.num == 5 else 0)
                    scroll_amount = -1 if delta > 0 else 1
                    canvas.yview_scroll(scroll_amount, "units")
                    return "break"
            except:
                pass
        
        def element_drag_start(event):
            if event.num == 1:  # Left button
                self._drag_start_y = event.y
                self._is_dragging = True
                return "break"
        
        def element_drag_end(event):
            if event.num == 1:  # Left button
                self._is_dragging = False
                return "break"
        
        def element_drag_motion(event):
            if self._is_dragging:
                try:
                    if hasattr(self.chat_scrollable, '_parent_canvas'):
                        canvas = self.chat_scrollable._parent_canvas
                        delta_y = event.y - self._drag_start_y
                        scroll_units = int(-delta_y / 10)
                        
                        if scroll_units != 0:
                            canvas.yview_scroll(scroll_units, "units")
                            self._drag_start_y = event.y
                        
                        return "break"
                except:
                    pass
        
        try:
            # Mouse wheel events
            element.bind("<MouseWheel>", element_scroll, "+")
            element.bind("<Button-4>", element_scroll, "+")
            element.bind("<Button-5>", element_scroll, "+")
            
            # Click and drag events
            element.bind("<Button-1>", element_drag_start, "+")
            element.bind("<ButtonRelease-1>", element_drag_end, "+")
            element.bind("<B1-Motion>", element_drag_motion, "+")
        except:
            pass
    
    def _apply_wheel_scroll_to_element(self, element) -> None:
        """Apply ONLY wheel scroll to element (for buttons - preserves click functionality)"""
        def element_scroll(event):
            try:
                if hasattr(self.chat_scrollable, '_parent_canvas'):
                    canvas = self.chat_scrollable._parent_canvas
                    delta = event.delta if hasattr(event, 'delta') else (120 if event.num == 4 else -120 if event.num == 5 else 0)
                    scroll_amount = -1 if delta > 0 else 1
                    canvas.yview_scroll(scroll_amount, "units")
                    return "break"
            except:
                pass
        
        try:
            # ONLY mouse wheel events, no click/drag events
            element.bind("<MouseWheel>", element_scroll, "+")
            element.bind("<Button-4>", element_scroll, "+")
            element.bind("<Button-5>", element_scroll, "+")
        except:
            pass
    
    def _add_bot_message(self, message: str) -> None:
        """Add a bot message bubble to the chat"""
        
        # Message container (left aligned)
        msg_container = ctk.CTkFrame(self.chat_scrollable, fg_color="transparent")
        msg_container.pack(fill="x", pady=5)
        
        # Material Design Bot Bubble (left side)
        bubble_frame = ctk.CTkFrame(msg_container, fg_color=LIGHT_GRAY, corner_radius=12)
        bubble_frame.pack(side="left", padx=(0, 100))
        
        # Bot icon + message
        content_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Message text with increased wrap length for full recommendations
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=500,  # Increased for longer recommendations
            justify="left",
            anchor="w"
        )
        message_label.pack(fill="x")
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(
            content_frame,
            text=timestamp,
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        time_label.pack(anchor="w", pady=(5, 0))
        
        # Apply scroll to new message elements
        self._apply_scroll_to_element(msg_container)
        self._apply_scroll_to_element(bubble_frame)
        self._apply_scroll_to_element(message_label)
        
        # Smart scroll: bot messages go to bottom unless we're in AI response mode
        if not getattr(self, '_in_ai_response_mode', False):
            self.after(100, self._scroll_to_bottom)
    
    def _add_user_message(self, message: str) -> None:
        """Add a user message bubble to the chat"""
        
        # Message container (right aligned)
        msg_container = ctk.CTkFrame(self.chat_scrollable, fg_color="transparent")
        msg_container.pack(fill="x", pady=5)
        
        # Material Design User Bubble (right side)
        bubble_frame = ctk.CTkFrame(msg_container, fg_color=PRIMARY_BLUE, corner_radius=12)
        bubble_frame.pack(side="right", padx=(100, 0))
        
        # Message content
        content_frame = ctk.CTkFrame(bubble_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Message text
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color="white",
            wraplength=400,
            justify="right",
            anchor="e"
        )
        message_label.pack(fill="x")
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(
            content_frame,
            text=timestamp,
            font=ctk.CTkFont(size=10),
            text_color="#cccccc"
        )
        time_label.pack(anchor="e", pady=(5, 0))
        
        # Apply scroll to new user message elements
        self._apply_scroll_to_element(msg_container)
        self._apply_scroll_to_element(bubble_frame)
        self._apply_scroll_to_element(message_label)
        
        # Always auto-scroll for user messages
        self.after(100, self._scroll_to_bottom)
    
    def _show_question_buttons(self) -> None:
        """Show the question buttons menu"""
        
        # Get available general queries
        available_queries = self._chat_controller.get_available_queries()
        
        # Questions container
        questions_container = ctk.CTkFrame(self.chat_scrollable, fg_color="transparent")
        questions_container.pack(fill="x", pady=10)
        
        # Apply wheel scroll only to questions container (has buttons inside)
        self._apply_wheel_scroll_to_element(questions_container)
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
        
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
        self._show_loading_message(f"🤔 Analizando {query_key.replace('_', ' ').title()}...")
        self._chat_controller.execute_query_async(query_key)
    
    def _handle_search_click(self) -> None:
        """Handle search button click"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self._show_error_message("❌ Por favor, ingresa un ID o descripción de producto")
            return
        
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
        self.after(0, lambda: self._display_query_result(result))
    
    def _on_query_error(self, error_message: str) -> None:
        """Called when a query fails"""
        self.after(0, lambda: self._show_error_message(error_message))
    
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
    
<<<<<<< HEAD
    def reset_view_state(self):
        """Public method to reset view state when entering"""
        self._reset_to_initial_state()
    
    def go_back(self):
        """Return to previous view"""
        try:
            self.controlador.mostrar_vista(self.previous_view)
        except Exception as e:
            print(f"❌ Error de navegación: {e}")
=======
    def _format_data_summary(self, data_items: list) -> str:
        """Format data items for display"""
        summary_lines = []
        
        for i, item in enumerate(data_items, 1):
            if 'descripcion' in item:
                desc = item['descripcion']
                if 'stock_actual' in item:
                    summary_lines.append(f"{i}. **{desc}** - Stock: {item['stock_actual']}")
                elif 'ventas_mes' in item:
                    summary_lines.append(f"{i}. **{desc}** - Ventas: {item['ventas_mes']}")
                else:
                    summary_lines.append(f"{i}. **{desc}**")
            elif 'producto' in item:
                summary_lines.append(f"{i}. **{item['producto']}**")
            else:
                summary_lines.append(f"{i}. {str(item)[:50]}...")
        
        return "\n".join(summary_lines)
    
    def set_previous_view(self, view_name):
        """Establecer la vista anterior para navegación"""
        self.previous_view = view_name
    
    def go_back(self):
        """Volver a la vista anterior"""
        try:
            print(f"🔙 Regresando a vista: {self.previous_view}")
            self.controlador.mostrar_vista(self.previous_view)
        except Exception as e:
            print(f"❌ Error regresando a vista anterior: {e}")
            # Como fallback, ir a filtro
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
            self.controlador.mostrar_vista("filtro")
    
    def cleanup(self):
        """Handle cleanup when switching views"""
        try:
            if hasattr(self, '_chat_controller'):
<<<<<<< HEAD
=======
                # Cleanup controller if needed
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
                pass
        except Exception as e:
            print(f"Error during cleanup: {e}")


if __name__ == "__main__":
<<<<<<< HEAD
=======
    # Configure CustomTkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Test app - Create a simple test window
>>>>>>> 814cffca9df45649e361ad25989025e1e99ed59c
    print("ChatAIView es una vista integrada, no puede ejecutarse independientemente.")
    print("Para probar, ejecuta main.py")
