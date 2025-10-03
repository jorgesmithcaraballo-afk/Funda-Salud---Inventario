"""
Centralized icons system for the application
"""

# Navigation icons
ICON_HOME = "🏠"
ICON_CHAT = "💬" 
ICON_BACK = "◀"  # Better centered back arrow
ICON_TOOLS = "🛠️"
ICON_UPLOAD = "⬆️"

# Status icons
ICON_SUCCESS = "✅"
ICON_ERROR = "❌"
ICON_WARNING = "⚠️"
ICON_INFO = "ℹ️"
ICON_LOADING = "🔄"

# Action icons
ICON_SAVE = "💾"
ICON_EXPORT = "📊"
ICON_SEARCH = "🔍"
ICON_FILTER = "🔍"
ICON_SEND = "📤"
ICON_PLUS = "➕"
ICON_MINUS = "➖"

# Database icons
ICON_DATABASE = "🗄️"
ICON_TABLE = "📋"
ICON_USER = "👤"
ICON_USERS = "👥"

# System icons
ICON_SETTINGS = "⚙️"
ICON_CONFIG = "🔧"
ICON_LOCK = "🔒"
ICON_UNLOCK = "🔓"
ICON_KEY = "🔑"

# Medical/Health icons (for Fundación Salud)
ICON_HEALTH = "🏥"
ICON_MEDICAL = "⚕️"
ICON_MEDICINE = "💊"

# File icons
ICON_FILE = "📄"
ICON_FOLDER = "📁"
ICON_EXCEL = "📊"

# UI Elements
ICON_MENU = "☰"
ICON_CLOSE = "✕"
ICON_MINIMIZE = "−"
ICON_MAXIMIZE = "□"
ICON_FULLSCREEN = "⛶"

# Advanced arrows (better than ←)
ICON_BACK_ARROW = "◀"     # Main back arrow
ICON_BACK_ALT = "◄"       # Alternative back arrow  
ICON_FORWARD = "▶"        # Forward arrow
ICON_UP = "▲"             # Up arrow
ICON_DOWN = "▼"           # Down arrow
ICON_LEFT = "◀"           # Left arrow
ICON_RIGHT = "▶"          # Right arrow

# Status indicators
ICON_ONLINE = "🟢"
ICON_OFFLINE = "🔴"
ICON_PENDING = "🟡"
ICON_ACTIVE = "🟢"
ICON_INACTIVE = "⚪"

# Helper function to get consistent icon style
def get_icon_with_text(icon, text="", spacing=" "):
    """Get icon with optional text, properly spaced"""
    if text:
        return f"{icon}{spacing}{text}"
    return icon

# Common icon combinations
ICON_LOGIN = get_icon_with_text("🔐", "")
ICON_LOGOUT = get_icon_with_text("🚪", "")
ICON_INVENTORY = get_icon_with_text("📦", "")
ICON_REPORTS = get_icon_with_text("📊", "")
ICON_AI_CHAT = get_icon_with_text("🤖", "")
