"""
Sistema de gestión de rutas para recursos embebidos en PyInstaller.
Detecta automáticamente si la aplicación se ejecuta como .exe o como script Python.
"""
import os
import sys
from pathlib import Path
from typing import Union


def get_base_path() -> Path:
    """
    Obtiene el directorio base de la aplicación.
    
    Returns:
        Path: Directorio base según el modo de ejecución
              - Si es .exe: directorio temporal de PyInstaller (_MEIPASS)
              - Si es script: directorio del archivo principal
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Ejecutándose como .exe empaquetado por PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Ejecutándose como script Python normal
        return Path(__file__).parent.absolute()


def get_resource_path(relative_path: Union[str, Path]) -> Path:
    """
    Obtiene la ruta absoluta a un recurso, funciona tanto en desarrollo como en .exe
    
    Args:
        relative_path: Ruta relativa al recurso (ej: "img/logo.png")
    
    Returns:
        Path: Ruta absoluta al recurso
    
    Example:
        >>> logo_path = get_resource_path("img/logo.png")
        >>> icon_path = get_resource_path("img/icono.ico")
    """
    base_path = get_base_path()
    return base_path / relative_path


def get_data_directory() -> Path:
    """
    Obtiene el directorio donde se almacenan los datos persistentes (BD, logs, etc.)
    
    Returns:
        Path: Directorio de datos
              - Si es .exe: carpeta 'data' junto al ejecutable
              - Si es script: carpeta 'database' en el proyecto
    """
    if getattr(sys, 'frozen', False):
        # Modo .exe: usar carpeta 'data' junto al ejecutable
        exe_dir = Path(sys.executable).parent
        data_dir = exe_dir / "data"
    else:
        # Modo desarrollo: usar carpeta 'database' del proyecto
        data_dir = Path(__file__).parent / "database"
    
    # Crear directorio si no existe
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path(db_name: str = "sistema_inventario.db") -> Path:
    """
    Obtiene la ruta completa a la base de datos SQLite
    
    Args:
        db_name: Nombre del archivo de base de datos
    
    Returns:
        Path: Ruta completa a la base de datos
    """
    return get_data_directory() / db_name


def is_frozen() -> bool:
    """
    Verifica si la aplicación está ejecutándose como .exe empaquetado
    
    Returns:
        bool: True si es .exe, False si es script Python
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_app_directory() -> Path:
    """
    Obtiene el directorio donde está ubicado el ejecutable o script principal
    
    Returns:
        Path: Directorio de la aplicación
    """
    if getattr(sys, 'frozen', False):
        # Directorio del .exe
        return Path(sys.executable).parent
    else:
        # Directorio del script
        return Path(__file__).parent


# Funciones de conveniencia para recursos comunes
def get_logo_path() -> Path:
    """Obtiene la ruta al logo de la aplicación"""
    return get_resource_path("img/logo.png")


def get_icon_path() -> Path:
    """Obtiene la ruta al icono de la aplicación"""
    return get_resource_path("img/icono.ico")


def get_sql_structure_path() -> Path:
    """Obtiene la ruta al archivo SQL de estructura de BD"""
    return get_resource_path("database/estructura_bd.sql")


# Información de debug
def print_paths_info():
    """Imprime información útil sobre las rutas configuradas (para debugging)"""
    print("=" * 60)
    print("INFORMACIÓN DE RUTAS DE LA APLICACIÓN")
    print("=" * 60)
    print(f"Modo de ejecución: {'EJECUTABLE (.exe)' if is_frozen() else 'SCRIPT PYTHON'}")
    print(f"Directorio base: {get_base_path()}")
    print(f"Directorio de app: {get_app_directory()}")
    print(f"Directorio de datos: {get_data_directory()}")
    print(f"Base de datos: {get_database_path()}")
    print(f"Logo: {get_logo_path()}")
    print(f"Icono: {get_icon_path()}")
    print("=" * 60)


if __name__ == "__main__":
    # Test del módulo
    print_paths_info()
