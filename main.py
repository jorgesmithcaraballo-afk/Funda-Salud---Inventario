import os as _os_sys
import sys as _sys
# Garantizar que el root del proyecto esté en sys.path
_ROOT = _os_sys.path.dirname(__file__)
if _ROOT not in _sys.path:
    _sys.path.insert(0, _ROOT)

from views.configuracion_window import ConfiguracionView
from views.filtro_window import FiltroView
from views.login_window import LoginView
from views.subir_window import SubirView
from views.database_error_window import DatabaseErrorView
from views.chat_ai_window import ChatAIView
from resource.colors import (WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, 
                   get_window_geometry, get_header_button_style)
from tkinter import filedialog
import customtkinter as ctk
import mysql.connector
import logging
import os
from typing import Dict, Any, Optional

ICON_PATH = os.path.join("img", "icono.ico")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Inventario - Fundación Salud")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(True, True)  # Permitir redimensionar
        
        # Configurar tamaño mínimo
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Configurar para permitir pantalla completa
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        self.fullscreen_state = False
        
        # Window state system to preserve size between views
        self.window_state = {
            'geometry_set': False,  # Whether initial geometry was set
            'user_resized': False,  # Whether user manually resized window
            'current_view': None    # Current view for tracking
        }
        
        # Monitor size changes to detect manual resizing
        self.bind("<Configure>", self._on_window_configure)

        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)

        # Dictionary to store views
        self.frames = {}
        self.database_error = None

        # Initialize database automatically
        self.inicializar_base_datos()

    def inicializar_base_datos(self) -> None:
        """Inicializar y configurar MySQL automáticamente"""
        try:
            logger.info("🔄 Iniciando configuración automática de MySQL...")
            
            # Intentar conectar y crear la base de datos si es necesario
            from conexion import db_manager, crear_base_datos
            
            # Verificar si ya existe conexión
            if self.verificar_conexion_database():
                logger.info("✅ Base de datos MySQL ya configurada")
                self.registrar_vistas_principales()
                self.mostrar_vista("login")
                return
            
            # Si no existe, intentar crear automáticamente
            logger.info("🛠️ Configurando MySQL automáticamente...")
            
            # Intentar crear con diferentes credenciales root comunes
            mysql_creado = self.crear_mysql_automaticamente()
            
            if mysql_creado:
                logger.info("✅ MySQL configurado exitosamente")
                self.registrar_vistas_principales()
                self.mostrar_vista("login")
            else:
                logger.warning("⚠️ No se pudo configurar MySQL automáticamente")
                self.registrar_vista_error()
                self.mostrar_vista("database_error")
                
        except Exception as e:
            logger.error(f"❌ Error en inicialización: {e}")
            self.database_error = str(e)
            self.registrar_vista_error()
            self.mostrar_vista("database_error")

    def crear_mysql_automaticamente(self) -> bool:
        """Crear base de datos MySQL automáticamente con credenciales comunes"""
        from config import db_config
        credenciales_root = db_config.ROOT_CREDENTIALS
        
        for usuario, password in credenciales_root:
            try:
                logger.info(f"🔑 Intentando conectar como {usuario}...")
                
                # Conectar como root
                root_conn = mysql.connector.connect(
                    host="localhost",
                    user=usuario,
                    password=password
                )
                
                cursor = root_conn.cursor()
                
                # Crear base de datos
                logger.info("🗄️ Creando base de datos 'sistema_inventario'...")
                cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_inventario")
                
                # Crear usuario 'fs'
                logger.info(f"👤 Creando usuario '{db_config.MYSQL_USER}'...")
                cursor.execute(f"DROP USER IF EXISTS '{db_config.MYSQL_USER}'@'localhost'")
                cursor.execute(f"CREATE USER '{db_config.MYSQL_USER}'@'localhost' IDENTIFIED BY '{db_config.MYSQL_PASSWORD}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON {db_config.MYSQL_DATABASE}.* TO '{db_config.MYSQL_USER}'@'localhost'")
                cursor.execute("FLUSH PRIVILEGES")
                
                cursor.close()
                root_conn.close()
                
                # Crear estructura de tablas
                logger.info("📋 Creando estructura de tablas...")
                from conexion import crear_base_datos
                crear_base_datos()
                
                logger.info("✅ ¡MySQL configurado exitosamente!")
                return True
                
            except mysql.connector.Error as e:
                logger.debug(f"❌ Falló conexión con {usuario}: {e}")
                continue
            except Exception as e:
                logger.debug(f"❌ Error inesperado con {usuario}: {e}")
                continue
        
        logger.error("❌ No se pudo conectar con ninguna credencial root común")
        return False

    def verificar_conexion_database(self) -> bool:
        """Verificar si se puede conectar a la base de datos"""
        try:
            from conexion import obtener_conexion
            conn = obtener_conexion()
            conn.close()
            logger.info("Conexión a base de datos exitosa")
            return True
        except mysql.connector.Error as e:
            logger.error(f"Error de conexión a base de datos: {e}")
            self.database_error = str(e)
            return False
        except Exception as e:
            logger.error(f"Error inesperado al conectar a base de datos: {e}")
            self.database_error = str(e)
            return False

    def registrar_vistas_principales(self) -> None:
        """Registrar todas las vistas principales de la aplicación"""
        try:
            self.registrar_vista("login", LoginView)
            self.registrar_vista("chat_ai", ChatAIView)
            self.registrar_vista("subir", SubirView)
            self.registrar_vista("configuracion", ConfiguracionView)
            
            # FiltroView requiere conexión DB, manejar separadamente
            self.registrar_vista("filtro", FiltroView)
            
        except Exception as e:
            logger.error(f"Error registrando vistas: {e}")
            # Si hay error registrando vistas, mostrar error de DB
            self.registrar_vista_error()
            self.mostrar_vista("database_error")

    def registrar_vista_error(self) -> None:
        """Registrar solo la vista de error de base de datos"""
        try:
            frame = DatabaseErrorView(self, self, self.database_error or "Error de conexión desconocido")
            self.frames["database_error"] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        except Exception as e:
            logger.error(f"Error crítico registrando vista de error: {e}")
            # Como último recurso, mostrar mensaje básico
            import tkinter.messagebox as mb
            mb.showerror(
                "Error Crítico",
                f"No se pudo inicializar la aplicación:\n{str(e)}\n\n"
                "Contacte al administrador del sistema."
            )
            self.quit()

    def registrar_vista(self, nombre: str, clase_vista: type) -> None:
        frame = clase_vista(self, self)
        self.frames[nombre] = frame
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Mantener la vista oculta hasta que se seleccione explícitamente con mostrar_vista
        try:
            frame.lower()
        except Exception:
            pass

    def toggle_fullscreen(self, event: Optional[Any] = None) -> str:
        """Alternar pantalla completa con F11"""
        self.fullscreen_state = not self.fullscreen_state
        self.attributes("-fullscreen", self.fullscreen_state)
        
        # Mark as user-resized when exiting fullscreen
        if not self.fullscreen_state:
            self.window_state['user_resized'] = True
            
        return "break"

    def exit_fullscreen(self, event: Optional[Any] = None) -> str:
        """Salir de pantalla completa con Escape"""
        self.fullscreen_state = False
        self.attributes("-fullscreen", False)
        
        # Mark as user-resized
        self.window_state['user_resized'] = True
        
        return "break"

    def _on_window_configure(self, event: Any) -> None:
        """Detect when user manually resizes the window"""
        if event.widget == self:  # Only main window events
            # If initial geometry was set, any change is from user
            if self.window_state['geometry_set']:
                self.window_state['user_resized'] = True

    def mostrar_vista(self, nombre: str, vista_anterior: Optional[str] = None) -> None:
        """Show view preserving current window state"""
        
        # Save previous view for navigation
        if vista_anterior:
            if hasattr(self.frames.get(nombre), 'set_previous_view'):
                self.frames[nombre].set_previous_view(vista_anterior)
        
        # Reset view state if method exists
        if hasattr(self.frames.get(nombre), 'reset_view_state'):
            self.frames[nombre].reset_view_state()
        
        # Only apply fixed geometry if:
        # 1. Not in fullscreen mode
        # 2. User hasn't manually resized
        # 3. First view or initial change
        if (not self.fullscreen_state and 
            not self.window_state['user_resized'] and 
            not self.window_state['geometry_set']):
            
            geometry = get_window_geometry(nombre)
            self.geometry(geometry)
            self.window_state['geometry_set'] = True
            
        # Update current view
        self.window_state['current_view'] = nombre

        # Show the view
        for vista in self.frames.values():
            vista.lower()
        self.frames[nombre].lift()


if __name__ == "__main__":
    app = App()
    app.mainloop()
