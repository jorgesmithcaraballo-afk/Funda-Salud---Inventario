"""
Centralized application configuration
Contains all hardcoded values and settings in one place
"""
import os
from typing import Dict, List, Tuple


class DatabaseConfig:
    """Database connection configuration"""
    
    # MySQL Configuration
    MYSQL_HOST = "localhost"
    MYSQL_USER = "fs"
    MYSQL_PASSWORD = "Gato7Sol"
    MYSQL_DATABASE = "sistema_inventario"
    
    # Connection settings
    CONNECTION_TIMEOUT = 10
    
    # Common root credentials to try during auto-setup
    ROOT_CREDENTIALS: List[Tuple[str, str]] = [
        ("root", ""),
        ("root", "root"),
        ("root", "admin"),
        ("root", "password"),
        ("root", "mysql"),
        ("root", "123456")
    ]
    
    @classmethod
    def get_mysql_config(cls) -> Dict[str, str]:
        """Get MySQL connection dictionary"""
        return {
            "host": cls.MYSQL_HOST,
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "database": cls.MYSQL_DATABASE,
            # Set connection timeout to prevent UI freezes when DB is unreachable
            "connection_timeout": cls.CONNECTION_TIMEOUT,
        }


class AppConfig:
    """Application-wide configuration"""
    
    # App info
    APP_NAME = "Sistema de Inventario - Fundación Salud"
    VERSION = "1.0.0"
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMG_DIR = os.path.join(BASE_DIR, "img")
    DATABASE_DIR = os.path.join(BASE_DIR, "database")
    
    # File paths
    LOGO_PATH = os.path.join(IMG_DIR, "logo.png")
    ICON_PATH = os.path.join(IMG_DIR, "icono.ico")
    SQL_STRUCTURE_PATH = os.path.join(BASE_DIR, "estructura_bd.sql")
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(levelname)s:%(name)s:%(message)s"
    
    # GUI Settings
    APPEARANCE_MODE = "light"
    COLOR_THEME = "blue"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        for directory in [cls.IMG_DIR, cls.DATABASE_DIR]:
            os.makedirs(directory, exist_ok=True)


class UIConfig:
    """UI-specific configuration"""
    
    # Threading
    THREAD_TIMEOUT = 30
    
    # UI Updates
    AUTO_RETRY_DELAY = 3000  # milliseconds


# Global instances for easy access
db_config = DatabaseConfig()
app_config = AppConfig()
ui_config = UIConfig()

# Ensure directories exist on import
app_config.ensure_directories()
