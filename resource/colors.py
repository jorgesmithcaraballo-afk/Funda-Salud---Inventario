"""
Unified color system for the application
"""

# Primary colors from original app
PRIMARY_BLUE = "#004aad"
PRIMARY_BLUE_DARK = "#00367d"

# Basic colors
WHITE = "#ffffff"
LIGHT_GRAY = "#f5f5f5"
BLACK = "#000000"
GRAY = "#cccccc"

# Status colors
SUCCESS_GREEN = "#2e7d32"
SUCCESS_GREEN_HOVER = "#1b5e20"
ERROR_RED = "#d32f2f"
ERROR_RED_BG = "#ffebee"

# Headers
HEADER_BG = PRIMARY_BLUE
HEADER_TEXT = WHITE
HEADER_BUTTON_BG = WHITE
HEADER_BUTTON_TEXT = BLACK
HEADER_BUTTON_HOVER = GRAY

# Buttons
BUTTON_PRIMARY_BG = PRIMARY_BLUE
BUTTON_PRIMARY_HOVER = PRIMARY_BLUE_DARK
BUTTON_PRIMARY_TEXT = WHITE

BUTTON_HEADER_BG = WHITE
BUTTON_HEADER_TEXT = BLACK
BUTTON_HEADER_HOVER = GRAY

BUTTON_SUCCESS_BG = SUCCESS_GREEN
BUTTON_SUCCESS_HOVER = SUCCESS_GREEN_HOVER
BUTTON_SUCCESS_TEXT = WHITE

# Backgrounds
VIEW_BACKGROUND = WHITE
PANEL_RIGHT_BG = PRIMARY_BLUE
CHAT_BACKGROUND = LIGHT_GRAY
TABLE_ROW_ALT_BG = "#f9f9f9"

# Inputs
INPUT_BG = WHITE
INPUT_BORDER = LIGHT_GRAY
INPUT_TEXT = BLACK

# Text colors
TEXT_PRIMARY = "#212121"
TEXT_SECONDARY = "#757575"

# Window sizes
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Helper functions
def get_header_button_style():
    """Standard style for header buttons"""
    return {
        "width": 45,
        "height": 45,
        "corner_radius": 25,
        "fg_color": BUTTON_HEADER_BG,
        "text_color": BUTTON_HEADER_TEXT,
        "hover_color": BUTTON_HEADER_HOVER,
        "font": ("Arial", 22)
    }

def get_window_geometry(view_name="default"):
    """Get unified window geometry"""
    return f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
