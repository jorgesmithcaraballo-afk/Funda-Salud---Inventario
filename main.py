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
from resource.sizes import WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from resource.colors import get_window_geometry
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

        # Permitir redimensionamiento (comportamiento previo, evita caja pequeña)
        self.resizable(True, True)

        # Configurar tamaño mínimo (antes de maximizar para evitar que se haga muy pequeña)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # --- Ventana maximizada en inicio ---
        if _sys.platform.startswith("win"):
            # Windows soporta "zoomed"
            self.state("zoomed")
        else:
            # macOS / Linux: usar tamaño completo de la pantalla
            self.update_idletasks()  # asegura cálculo correcto de screen size
            w, h = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")

        # Nota: no forzar relación de aspecto para permitir maximizar libremente en macOS/Windows
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.background = ctk.CTkFrame(self, fg_color="white")
        
        # Re-aplicar maximización cuando el loop está listo (macOS/Linux)
        # Esto evita casos donde el gestor de ventanas reajusta el tamaño inicial.
        self.after(0, self._maximize_startup)
        # Enforce maximized once when the window is mapped (macOS safety)
        try:
            self._max_enforced = False
            self.bind("<Map>", self._on_map_enforce_max)
        except Exception:
            pass

        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(ICON_PATH)
            except Exception:
                logger.warning("No se pudo cargar el ícono en este sistema.")

        # Diccionario para almacenar vistas
        self.frames: Dict[str, ctk.CTkFrame] = {}
        self.database_error: Optional[str] = None

        # Inicializar base de datos
        self.inicializar_base_datos()

    def inicializar_base_datos(self) -> None:
        """Inicializar y configurar MySQL automáticamente"""
        try:
            logger.info("🔄 Iniciando configuración automática de MySQL...")

            from conexion import db_manager, crear_base_datos

            if self.verificar_conexion_database():
                logger.info("✅ Base de datos MySQL ya configurada")
                self.registrar_vistas_principales()
                self.mostrar_vista("login")
                return

            logger.info("🛠️ Configurando MySQL automáticamente...")
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

                root_conn = mysql.connector.connect(
                    host="localhost",
                    user=usuario,
                    password=password
                )
                cursor = root_conn.cursor()

                logger.info("🗄️ Creando base de datos 'sistema_inventario'...")
                cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_inventario")

                logger.info(f"👤 Creando usuario '{db_config.MYSQL_USER}'...")
                cursor.execute(f"DROP USER IF EXISTS '{db_config.MYSQL_USER}'@'localhost'")
                cursor.execute(
                    f"CREATE USER '{db_config.MYSQL_USER}'@'localhost' "
                    f"IDENTIFIED BY '{db_config.MYSQL_PASSWORD}'"
                )
                cursor.execute(
                    f"GRANT ALL PRIVILEGES ON {db_config.MYSQL_DATABASE}.* "
                    f"TO '{db_config.MYSQL_USER}'@'localhost'"
                )
                cursor.execute("FLUSH PRIVILEGES")

                cursor.close()
                root_conn.close()

                logger.info("📋 Creando estructura de tablas...")
                from conexion import crear_base_datos
                crear_base_datos()

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
        try:
            self.registrar_vista("login", LoginView)
            self.registrar_vista("chat_ai", ChatAIView)
            self.registrar_vista("subir", SubirView)
            self.registrar_vista("configuracion", ConfiguracionView)
            self.registrar_vista("filtro", FiltroView)
        except Exception as e:
            logger.error(f"Error registrando vistas: {e}")
            self.registrar_vista_error()
            self.mostrar_vista("database_error")

    def registrar_vista_error(self) -> None:
        try:
            frame = DatabaseErrorView(self, self, self.database_error or "Error de conexión desconocido")
            self.frames["database_error"] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        except Exception as e:
            logger.error(f"Error crítico registrando vista de error: {e}")
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
        frame.grid(row=0, column=0, sticky="nsew")
        try:
            frame.lower()
        except Exception:
            pass

    def mostrar_vista(self, nombre: str, vista_anterior: Optional[str] = None) -> None:
        if vista_anterior:
            if hasattr(self.frames.get(nombre), 'set_previous_view'):
                self.frames[nombre].set_previous_view(vista_anterior)

        if hasattr(self.frames.get(nombre), 'reset_view_state'):
            self.frames[nombre].reset_view_state()

        self.window_state = {"current_view": nombre}

        for vista in self.frames.values():
            vista.lower()
        self.frames[nombre].lift()

    def _maximize_startup(self) -> None:
        """Apply maximized geometry once the event loop is running."""
        try:
            if _sys.platform.startswith("win"):
                # Re-aplicar zoomed por si el gestor de ventanas cambió el estado
                self.state("zoomed")
            else:
                # En macOS/Linux calcular tamaño de pantalla y aplicar geometría
                try:
                    self.update_idletasks()
                except Exception:
                    pass
                w, h = self.winfo_screenwidth(), self.winfo_screenheight()
                try:
                    self.geometry(f"{w}x{h}+0+0")
                except Exception:
                    pass
            # Reaplicar mínimos/aspecto tras maximizar
            try:
                self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
            except Exception:
                pass
        except Exception:
            # Evitar que un fallo aquí impida abrir la app
            pass

    def _on_map_enforce_max(self, _evt=None) -> None:
        """Enforce maximize once when window gets mapped to the screen (macOS)."""
        if getattr(self, "_max_enforced", False):
            return
        try:
            self._maximize_startup()
            self._max_enforced = True
        except Exception:
            pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
