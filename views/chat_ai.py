"""
🤖 Chat IA WhatsApp Style - Sistema de Inventario
UI tipo WhatsApp con flujo conversacional inteligente
"""

import customtkinter as ctk
import threading
from typing import Optional, Dict, Any
from datetime import datetime
from controllers.chat_controller import ChatController
from models.inventory_models import QueryResult

# AI Configuration - PUT YOUR GEMINI API KEY HERE
API_KEY = "AIzaSyBWx-YLBoGowxRBJqO-oenJX3aeZ9J9Zvg"

# Material Design Color Palette
PRIMARY_BLUE = "#1976d2"      # Material Blue 700
LIGHT_BLUE = "#bbdefb"        # Material Blue 100
SURFACE_WHITE = "#ffffff"     # Material Surface
BACKGROUND_GREY = "#f5f5f5"   # Material Background
TEXT_PRIMARY = "#212121"      # Material Text Primary
TEXT_SECONDARY = "#757575"    # Material Text Secondary
SUCCESS_GREEN = "#4caf50"     # Material Green 500
ACCENT_TEAL = "#009688"       # Material Teal 500

class ChatAIView(ctk.CTk):
    """Main WhatsApp-style chat application for inventory management"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("🤖 Chat IA - Sistema de Inventario")
        self.geometry("800x700")
        self.resizable(True, True)
        
        # Chat state - simplified without product-specific mode
        self.current_mode = "general"  # Always general mode
        
        # Initialize controller
        self._chat_controller = ChatController(API_KEY)
        self._setup_controller_callbacks()
        
        # Setup UI
        self._setup_ui()
        
        # Start conversation
        self._add_bot_message("¡Hola! 👋 Soy tu asistente de inventario")
        self._add_bot_message("Selecciona una de las siguientes opciones para comenzar:")
        self._show_question_buttons()
        
        # Ensure scroll is working after initial setup
        self.after(500, self._ensure_scroll_working)
    
    def _setup_controller_callbacks(self) -> None:
        """Setup callbacks for the chat controller"""
        self._chat_controller.set_query_callbacks(
            on_started=self._on_query_started,
            on_completed=self._on_query_completed,
            on_error=self._on_query_error
        )
    
    def _setup_ui(self) -> None:
        """Setup the WhatsApp-style chat UI"""
        
        # Material Design Header
        header_frame = ctk.CTkFrame(self, fg_color=PRIMARY_BLUE, height=70)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            header_content,
            text="🤖 Asistente IA - Inventario",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left")
        
        # AI status
        status_text = "🟢 IA Activa" if self._chat_controller.is_ai_configured() else "🟡 IA Básica"
        status_label = ctk.CTkLabel(
            header_content,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        status_label.pack(side="right")
        
        # Main chat area
        self._setup_chat_area()
        
        # Input area (initially hidden, will be shown when needed)
        self._setup_input_area()
    
    def _setup_chat_area(self) -> None:
        """Setup the scrollable chat messages area"""
        
        # Material Design Chat Container
        chat_container = ctk.CTkFrame(self, fg_color=SURFACE_WHITE)
        chat_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Material Design Scrollable Chat Frame
        self.chat_scrollable = ctk.CTkScrollableFrame(
            chat_container,
            fg_color=SURFACE_WHITE,
            scrollbar_button_color=PRIMARY_BLUE,
            scrollbar_button_hover_color="#1565c0"
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
        
        self.input_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_GREY, height=80)
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
            height=40
        )
        self.text_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Send button
        self.send_button = ctk.CTkButton(
            input_container,
            text="Enviar 📤",
            width=100,
            height=40,
            command=self._send_text_message,
            fg_color=SUCCESS_GREEN,
            hover_color="#43a047"
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
        self.bind_all("<MouseWheel>", on_mouse_wheel)
        self.bind_all("<Button-4>", on_mouse_wheel)
        self.bind_all("<Button-5>", on_mouse_wheel)
        
        # Bind click and drag events (disabled globally to avoid button interference)
        # self.bind_all("<Button-1>", on_button_press)
        # self.bind_all("<ButtonRelease-1>", on_button_release)
        # self.bind_all("<B1-Motion>", on_mouse_motion)
        
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
        bubble_frame = ctk.CTkFrame(msg_container, fg_color=BACKGROUND_GREY, corner_radius=12)
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
        
        # Title
        title_label = ctk.CTkLabel(
            questions_container,
            text="📋 Preguntas disponibles:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=20, pady=(0, 10))
        
        # Apply wheel scroll to title (inside button container, so no drag)
        self._apply_wheel_scroll_to_element(title_label)
        
        # Create buttons for each query
        button_order = [
            "low_stock", "expiring_soon", "expired_products", "top_selling", "low_rotation",
            "inventory_value", "price_changes", "excess_stock", "out_of_stock", "urgent_restock"
        ]
        
        # Only show the 10 general queries
        
        for query_key in button_order:
            if query_key in available_queries:
                query_info = available_queries[query_key]
                self._create_question_button(questions_container, query_key, query_info)
        
        # No back button needed - always in general mode
        
        # Auto-scroll to bottom
        self.after(100, self._scroll_to_bottom)
    
    def _create_question_button(self, parent, query_key: str, query_info: Dict[str, Any]) -> None:
        """Create a single question button"""
        
        # Material Design Button with subtle elevation
        btn = ctk.CTkButton(
            parent,
            text=query_info['title'],  # Clean, no-icon design
            font=ctk.CTkFont(size=13, weight="normal"),
            height=40,
            fg_color=query_info['color'],
            hover_color=self._darken_color(query_info['color']),
            command=lambda key=query_key: self._handle_question_click(key),
            corner_radius=8,  # Material Design corner radius
            border_width=0
        )
        btn.pack(fill="x", padx=16, pady=4)  # Material Design spacing
        
        # Apply ONLY wheel scroll to button (not drag, to preserve click functionality)
        self._apply_wheel_scroll_to_element(btn)
    
    def _handle_question_click(self, query_key: str) -> None:
        """Handle when a question button is clicked"""
        
        # Process query directly
        available_queries = self._chat_controller.get_available_queries()
        if query_key in available_queries:
            query_title = available_queries[query_key]['title']
            self._add_user_message(query_title)
            self._execute_query(query_key)
    
    def _execute_query(self, query_key: str) -> None:
        """Execute a query and show loading state"""
        # Set flags for smart scroll behavior
        self._in_ai_response_mode = True
        self._remember_scroll_position()
        
        self._add_bot_message("🤔 Analizando datos...")
        self._chat_controller.execute_query_async(query_key)
    
    def _send_text_message(self) -> None:
        """Send text message (not used in simplified version)"""
        pass  # Simplified version doesn't use text input
    
    def _show_input_area(self) -> None:
        """Show the text input area"""
        self.input_frame.pack(fill="x", padx=10, pady=10)
        self.text_entry.focus()
    
    def _hide_input_area(self) -> None:
        """Hide the text input area"""
        self.input_frame.pack_forget()
    
    
    def _remember_scroll_position(self) -> None:
        """Remember current scroll position before adding response"""
        try:
            # Get current number of children (messages) in chat
            self.response_start_position = len(self.chat_scrollable.winfo_children())
        except:
            self.response_start_position = 0
    
    def _scroll_to_response(self) -> None:
        """Scroll to the beginning of the AI response (not to bottom)"""
        try:
            if hasattr(self, 'response_start_position'):
                # Get all children widgets
                children = self.chat_scrollable.winfo_children()
                
                if len(children) > self.response_start_position:
                    # Get the response message widget (the one at response_start_position)
                    response_widget = children[self.response_start_position]
                    
                    # Get the position of this widget relative to the scrollable frame
                    response_widget.update_idletasks()  # Ensure layout is complete
                    
                    # Calculate the Y position of the response widget
                    widget_y = response_widget.winfo_y()
                    
                    # Get total scrollable height
                    canvas = self.chat_scrollable._parent_canvas
                    scrollable_height = self.chat_scrollable.winfo_reqheight()
                    canvas_height = canvas.winfo_height()
                    
                    if scrollable_height > canvas_height:
                        # Calculate scroll ratio to show the response widget at the top
                        scroll_ratio = widget_y / max(1, scrollable_height - canvas_height)
                        scroll_ratio = max(0.0, min(1.0, scroll_ratio))
                        canvas.yview_moveto(scroll_ratio)
                    else:
                        # If content fits in view, scroll to top
                        canvas.yview_moveto(0.0)
                else:
                    # Fallback: scroll to middle
                    self.chat_scrollable._parent_canvas.yview_moveto(0.6)
            else:
                # Fallback: scroll to middle
                self.chat_scrollable._parent_canvas.yview_moveto(0.6)
        except Exception as e:
            print(f"Scroll error: {e}")
            # Safe fallback
            try:
                self.chat_scrollable._parent_canvas.yview_moveto(0.6)
            except:
                pass
    
    def _scroll_to_bottom(self) -> None:
        """Auto-scroll chat to bottom"""
        try:
            self.chat_scrollable._parent_canvas.yview_moveto(1.0)
        except:
            pass
    
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
        self.after(0, lambda: self._display_error(error_message))
    
    def _display_query_result(self, result: QueryResult) -> None:
        """Display the query result with smart scroll and consistent formatting"""
        
        # Show the AI response (already formatted by ResponseFormatter)
        if result.ai_response:
            self._add_bot_message(result.ai_response)
        else:
            self._add_bot_message(f"📊 Consulta completada. Se encontraron {len(result.data)} registros.")
        
        # Exit AI response mode before showing follow-up
        self._in_ai_response_mode = False
        
        # Show follow-up question
        self._add_bot_message("¿Qué más te gustaría consultar?")
        self._show_question_buttons()
        
        # Smart scroll: scroll to the beginning of AI response, not bottom
        self.after(200, self._scroll_to_response)
    
    def _display_error(self, error_message: str) -> None:
        """Display an error message with smart scroll"""
        self._add_bot_message(f"❌ {error_message}")
        
        # Exit AI response mode
        self._in_ai_response_mode = False
        
        self._add_bot_message("¿Te gustaría intentar con otra consulta?")
        self._show_question_buttons()
    
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


if __name__ == "__main__":
    # Configure CustomTkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Run app
    app = WhatsAppChatApp()
    app.mainloop()
