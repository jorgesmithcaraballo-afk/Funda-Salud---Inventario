"""
Unified color system for the application
"""

from resource.sizes import CONTENT_BUTTON_WIDTH, BUTTON_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT

# =============================
# Básicos
# =============================
WHITE = "#ffffff"
LIGHT_GRAY = "#f5f5f5"
BLACK = "#000000"
GRAY = "#cccccc"
DARK_GRAY = "#8d8d8d"

# =============================
# Paleta primaria (Azules)
# =============================
PRIMARY_BLUE = "#004aad"
PRIMARY_BLUE_DARK = "#00367d"
SECONDARY_BLUE = "#1976d2"
SECONDARY_BLUE_HOVER = "#1565c0"

# =============================
# Estados / Semánticos
# =============================
SUCCESS_GREEN = "#2e7d32"
SUCCESS_GREEN_HOVER = "#1b5e20"
ERROR_RED = "#d32f2f"
ERROR_RED_BG = "#ffebee"
DANGER_RED = "#c0392b"
DANGER_RED_HOVER = "#a93226"

# =============================
# Superficies y bordes
# =============================
NEUTRAL_BORDER = "#e0e0e0"
CARD_BG = "#f0f0f0"
SURFACE_LIGHT = "#f1f1f1"
TABLE_ROW_ALT_BG = "#f9f9f9"

# =============================
# Fondos
# =============================
VIEW_BACKGROUND = WHITE

# =============================
# Texto
# =============================
TEXT_PRIMARY = "#212121"   # principal (negro)
TEXT_DARK = "#222222"       # títulos
TEXT_MUTED = "#666666"      # descripciones/secondary
ERROR_TEXT_RED = "#cc0000"  # error


# (Eliminadas paletas alternas de verde; usar SUCCESS_GREEN/SUCCESS_GREEN_HOVER)

# Helper functions
def get_header_button_style():
    """Standard style for header buttons"""
    return {
        "width": 45,
        "height": 45,
        "corner_radius": 25,
        "fg_color": WHITE,
        "text_color": BLACK,
        "hover_color": GRAY,
        "font": ("Arial", 22)
    }

def get_content_button_style():
    """Standard style for main content buttons"""
    return {
        "width": CONTENT_BUTTON_WIDTH,
        "height": BUTTON_HEIGHT,
        "corner_radius": 8,
        "fg_color": SECONDARY_BLUE,
        "text_color": WHITE,
        "hover_color": SECONDARY_BLUE_HOVER,
        "font": ("Arial", 18)
    }

def get_window_geometry(view_name="default"):
    """Get unified window geometry"""
    return f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
