# conexion.py
import mysql.connector
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

# Import centralized configuration
from config import db_config
from typing import Optional

# Configuración de base de datos
DATABASE_TYPE = "mysql"  # Forzar uso de MySQL únicamente
SQLITE_DB_PATH = os.path.join("database", "sistema_inventario.db")
MYSQL_CONFIG = db_config.get_mysql_config()


class DatabaseManager:
    """Gestor de conexiones que maneja tanto MySQL como SQLite"""
    
    def __init__(self):
        self.db_type = self._detect_database_type()
        logger.info(f"Tipo de base de datos detectado: {self.db_type}")
    
    def _detect_database_type(self):
        """Detectar qué tipo de base de datos usar"""
        if DATABASE_TYPE != "auto":
            return DATABASE_TYPE
            
        # 1. Intentar SQLite primero (más simple)
        if os.path.exists(SQLITE_DB_PATH):
            try:
                conn = sqlite3.connect(SQLITE_DB_PATH)
                # Verificar si tiene las tablas necesarias
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='personal'")
                if cursor.fetchone():
                    conn.close()
                    return "sqlite"
                conn.close()
            except Exception as e:
                logger.warning(f"Error verificando SQLite: {e}")
        
        # 2. Si no hay SQLite, intentar MySQL
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            conn.close()
            return "mysql"
        except Exception as e:
            logger.warning(f"Error conectando a MySQL: {e}")
        
        # 3. Por defecto, usar SQLite (se creará si no existe)
        return "sqlite"
    
    def get_connection(self):
        """Obtener conexión según el tipo de BD configurado"""
        if self.db_type == "sqlite":
            return self._get_sqlite_connection()
        elif self.db_type == "mysql":
            return self._get_mysql_connection()
        else:
            raise Exception(f"Tipo de base de datos no soportado: {self.db_type}")
    
    def _get_sqlite_connection(self):
        """Conexión a SQLite"""
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(SQLITE_DB_PATH)
        # Configurar SQLite para que sea más compatible con MySQL
        conn.row_factory = sqlite3.Row
        return conn
    
    def _get_mysql_connection(self):
        """Conexión a MySQL"""
        return mysql.connector.connect(**MYSQL_CONFIG)
    
    def create_database_structure(self):
        """Crear estructura de base de datos"""
        if self.db_type == "sqlite":
            self._create_sqlite_structure()
        elif self.db_type == "mysql":
            self._create_mysql_structure()
    
    def _create_sqlite_structure(self):
        """Crear estructura SQLite"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Crear tabla 'personal'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                tiempo INTEGER,
                contrasena VARCHAR(128) NOT NULL,
                tipo VARCHAR(10) NOT NULL DEFAULT 'user'
            )
        ''')
        
        # Crear tabla padre 'Inventario'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion_insumo VARCHAR(255),
                tipo VARCHAR(25),
                cantidad INTEGER,
                costo_unitario DECIMAL(10, 2),
                monto_total DECIMAL(10, 2),
                categoria VARCHAR(50) NOT NULL DEFAULT 'General'
            )
        ''')
        
        # Crear tablas hijas
        for tabla in ['existencia_inicial', 'entradas', 'salidas', 'existencia_final']:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS {tabla} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventario_id INTEGER,
                    nombre VARCHAR(50),
                    FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
                )
            '''.replace('{tabla}', tabla))

        # Catálogo de categorías (opcional, pero recomendado)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                nombre VARCHAR(50) PRIMARY KEY
            )
        ''')
        # Semilla: asegurar 'General'
        cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES ('General')")
        
        # Crear usuario administrador por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM personal WHERE nombre = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO personal (nombre, apellido, tiempo, contrasena, tipo) 
                VALUES ('admin', 'sistema', 60, 'admin123', 'admin')
            ''')
        
        # Asegurar columna 'tipo' y actualizar valores requeridos
        try:
            self._ensure_personal_tipo(conn, cursor)
        except Exception as e:
            logger.warning(f"No se pudo asegurar columna 'tipo' en SQLite: {e}")

        # Asegurar columna categoria y normalizar
        try:
            self._ensure_inventario_categoria(conn, cursor)
        except Exception as e:
            logger.warning(f"No se pudo asegurar columna 'categoria' en SQLite: {e}")

        # Sincronizar categorías desde Inventario hacia catálogo (si faltan)
        try:
            self._sync_categories_from_inventory(conn, cursor)
        except Exception as e:
            logger.warning(f"No se pudo sincronizar categorías (SQLite): {e}")

        conn.commit()
        conn.close()
        logger.info("Estructura SQLite creada correctamente")
    
    def _create_mysql_structure(self):
        """Crear estructura MySQL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Leer y ejecutar script SQL
        script_path = os.path.join(os.path.dirname(__file__), "estructura_bd.sql")
        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            # Ejecutar cada comando SQL por separado
            sql_commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
            for command in sql_commands:
                if command:
                    cursor.execute(command)
            
            # Crear usuario administrador por defecto si no existe
            cursor.execute("SELECT COUNT(*) FROM personal WHERE nombre = 'admin'")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO personal (nombre, apellido, tiempo, contrasena) 
                    VALUES ('admin', 'sistema', 60, 'admin123')
                ''')
            
            # Asegurar columna 'tipo' y actualizar valores requeridos
            try:
                self._ensure_personal_tipo(conn, cursor)
            except Exception as e:
                logger.warning(f"No se pudo asegurar columna 'tipo' en MySQL: {e}")

            # Asegurar tamaño de columna contrasena para hashes
            try:
                self._ensure_password_length(conn, cursor)
            except Exception as e:
                logger.warning(f"No se pudo asegurar tamaño de 'contrasena' en MySQL: {e}")

            # Asegurar columna categoria en Inventario
            try:
                self._ensure_inventario_categoria(conn, cursor)
            except Exception as e:
                logger.warning(f"No se pudo asegurar columna 'categoria' en MySQL: {e}")

            # Crear catálogo de categorías y sincronizar
            try:
                self._ensure_categorias_table(conn, cursor)
                self._sync_categories_from_inventory(conn, cursor)
            except Exception as e:
                logger.warning(f"No se pudo crear/sincronizar catálogo de categorías (MySQL): {e}")

            conn.commit()
        except FileNotFoundError:
            logger.warning("No se encontró estructura_bd.sql, creando estructura básica")
            # Crear estructura básica si no hay archivo SQL
            cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_inventario")
            cursor.execute("USE sistema_inventario")
        
        conn.close()
        logger.info("Estructura MySQL creada correctamente")

    def _ensure_personal_tipo(self, conn, cursor) -> None:
        """Asegura que la tabla 'personal' tenga la columna 'tipo' y actualiza datos.

        - Agrega columna 'tipo' con DEFAULT 'user' si no existe.
        - Coloca 'naila' como 'admin' (case-insensitive en nombre).
        - Coloca el resto como 'user' si está NULL o distinto.
        """
        if self.db_type == "sqlite":
            # Verificar si columna existe
            cursor.execute("PRAGMA table_info(personal)")
            cols = [row[1] for row in cursor.fetchall()]  # (cid, name, type, ...)
            if 'tipo' not in cols:
                cursor.execute("ALTER TABLE personal ADD COLUMN tipo VARCHAR(10) NOT NULL DEFAULT 'user'")

            # Normalizar valores
            cursor.execute("UPDATE personal SET tipo = 'admin' WHERE LOWER(nombre) = 'naila'")
            cursor.execute("UPDATE personal SET tipo = 'user' WHERE LOWER(nombre) <> 'naila' OR tipo IS NULL")

    def _ensure_password_length(self, conn, cursor) -> None:
        """Asegura que la columna 'contrasena' soporte hashes (VARCHAR(128))."""
        if self.db_type == "sqlite":
            # SQLite no aplica estrictamente longitudes, pero validamos existencia de columna.
            # No es necesario migrar, el tipo ya fue ajustado en CREATE TABLE.
            return

        if self.db_type == "mysql":
            db_name = MYSQL_CONFIG.get('database')
            # Consultar longitud actual de la columna
            cursor.execute(
                """
                SELECT CHARACTER_MAXIMUM_LENGTH 
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'personal' AND COLUMN_NAME = 'contrasena'
                """,
                (db_name,)
            )
            row = cursor.fetchone()
            current_len = row[0] if row else None
            if current_len is None or current_len < 128:
                cursor.execute("ALTER TABLE personal MODIFY contrasena VARCHAR(128) NOT NULL")
            return

        if self.db_type == "mysql":
            # Determinar base de datos actual
            db_name = MYSQL_CONFIG.get('database')
            # Comprobar existencia de columna en INFORMATION_SCHEMA
            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'personal' AND COLUMN_NAME = 'tipo'
                """,
                (db_name,)
            )
            exists = cursor.fetchone()[0] > 0
            if not exists:
                cursor.execute("ALTER TABLE personal ADD COLUMN tipo VARCHAR(10) NOT NULL DEFAULT 'user'")

            # Normalizar valores
            cursor.execute("UPDATE personal SET tipo = 'admin' WHERE LOWER(nombre) = 'naila'")
            cursor.execute("UPDATE personal SET tipo = 'user' WHERE LOWER(nombre) <> 'naila' OR tipo IS NULL")

    def _ensure_inventario_categoria(self, conn, cursor) -> None:
        """Asegura que Inventario.categoria exista y tenga DEFAULT 'General'; normaliza nulos/vacíos."""
        if self.db_type == "sqlite":
            # En SQLite, si la columna no existe, intentar ALTER
            cursor.execute("PRAGMA table_info(Inventario)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'categoria' not in cols:
                try:
                    cursor.execute("ALTER TABLE Inventario ADD COLUMN categoria VARCHAR(50) NOT NULL DEFAULT 'General'")
                except Exception:
                    # Si falla el ALTER por versión antigua, ignoramos (la creación inicial ya la incluye)
                    pass
            # Normalizar
            cursor.execute("UPDATE Inventario SET categoria='General' WHERE categoria IS NULL OR TRIM(categoria) = ''")
            return

        if self.db_type == "mysql":
            db_name = MYSQL_CONFIG.get('database')
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA=%s AND TABLE_NAME='Inventario' AND COLUMN_NAME='categoria'
                """,
                (db_name,)
            )
            exists = cursor.fetchone()[0] > 0
            if not exists:
                cursor.execute("ALTER TABLE Inventario ADD COLUMN categoria VARCHAR(50) NOT NULL DEFAULT 'General'")
            # Normalizar
            cursor.execute("UPDATE Inventario SET categoria='General' WHERE categoria IS NULL OR TRIM(categoria) = ''")

    def _sync_categories_from_inventory(self, conn, cursor) -> None:
        """Sincroniza categorías distintas de Inventario hacia el catálogo 'categorias'."""
        try:
            if self.db_type == "sqlite":
                cursor.execute("INSERT OR IGNORE INTO categorias (nombre) SELECT DISTINCT COALESCE(NULLIF(TRIM(categoria), ''), 'General') FROM Inventario")
            else:
                cursor.execute("INSERT IGNORE INTO categorias (nombre) SELECT DISTINCT IFNULL(NULLIF(TRIM(categoria), ''), 'General') FROM Inventario")
        except Exception:
            # No interrumpir flujo si falla la sincronización
            pass

    # --- API pública para ejecutar migración desde fuera ---
    def run_personal_tipo_migration(self) -> bool:
        """Ejecuta la migración para asegurar columna 'tipo' en 'personal'."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            self._ensure_personal_tipo(conn, cursor)
            conn.commit()
            conn.close()
            logger.info("Migración de 'tipo' en 'personal' ejecutada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error ejecutando migración 'tipo' en 'personal': {e}")
            return False

def migracion_normalizar_categorias(reset_to_general: bool = True, drop_catalog: bool = True) -> bool:
    """Normaliza las categorías en toda la BD:
    - Si reset_to_general: establece Inventario.categoria = 'General' para todos los registros o cuando sea NULL/vacío.
    - Si drop_catalog: elimina la tabla 'categorias' si existe.

    Devuelve True si se completó sin excepciones.
    """
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        if reset_to_general:
            try:
                cursor.execute("UPDATE Inventario SET categoria='General' WHERE categoria IS NULL OR TRIM(categoria) = '' OR categoria <> 'General'")
            except Exception:
                # Si falla la columna por cualquier motivo, intentamos asegurarla y normalizar de nuevo
                try:
                    db_manager._ensure_inventario_categoria(conn, cursor)  # type: ignore[attr-defined]
                    cursor.execute("UPDATE Inventario SET categoria='General' WHERE categoria IS NULL OR TRIM(categoria) = '' OR categoria <> 'General'")
                except Exception:
                    pass

        if drop_catalog:
            try:
                cursor.execute("DROP TABLE IF EXISTS categorias")
            except Exception:
                pass

        conn.commit()
        conn.close()
        logger.info("Normalización de categorías completada (Inventario -> 'General')")
        return True
    except Exception as e:
        logger.error(f"Error normalizando categorías: {e}")
        return False

    def run_password_length_migration(self) -> bool:
        """Asegura que 'personal.contrasena' tenga longitud suficiente para hashes."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            self._ensure_password_length(conn, cursor)
            conn.commit()
            conn.close()
            logger.info("Migración de longitud de 'contrasena' ejecutada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error migrando longitud de 'contrasena': {e}")
            return False
    
    def migrate_to_sqlite(self):
        """Migrar datos de MySQL a SQLite si es posible"""
        if self.db_type != "sqlite":
            return False
            
        try:
            # Intentar conectar a MySQL para obtener datos
            mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
            mysql_cursor = mysql_conn.cursor(dictionary=True)
            
            # Obtener conexión SQLite
            sqlite_conn = self.get_connection()
            sqlite_cursor = sqlite_conn.cursor()
            
            # Migrar tabla personal
            mysql_cursor.execute("SELECT * FROM personal")
            personal_data = mysql_cursor.fetchall()
            
            for row in personal_data:
                sqlite_cursor.execute('''
                    INSERT OR REPLACE INTO personal (id, nombre, apellido, tiempo, contrasena, tipo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (row['id'], row['nombre'], row['apellido'], row['tiempo'], row['contrasena'], row['tipo']))
            
            # Migrar otras tablas según sea necesario...
            # (agregar lógica de migración para otras tablas)
            
            sqlite_conn.commit()
            mysql_conn.close()
            sqlite_conn.close()
            
            logger.info("Migración de MySQL a SQLite completada")
            return True
            
        except Exception as e:
            logger.warning(f"No se pudo migrar de MySQL a SQLite: {e}")
            return False


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()


def obtener_conexion():
    """Función de compatibilidad para obtener conexión"""
    return db_manager.get_connection()


def crear_base_datos():
    """Crear estructura de base de datos"""
    db_manager.create_database_structure()


def migracion_personal_tipo() -> bool:
    """Función pública para ejecutar la migración de columna 'tipo' en 'personal'."""
    return db_manager.run_personal_tipo_migration()


def get_database_type():
    """Obtener tipo de base de datos en uso"""
    return db_manager.db_type

def migrar_a_sqlite():
    """Migrar datos a SQLite si es posible"""
    return db_manager.migrate_to_sqlite()

def migracion_longitud_contrasena() -> bool:
    """Función pública para asegurar longitud de columna 'contrasena'."""
    return db_manager.run_password_length_migration()

def migracion_inventario_categoria() -> bool:
    """Función pública para asegurar columna Inventario.categoria y normalizar valores."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        db_manager._ensure_inventario_categoria(conn, cursor)  # type: ignore[attr-defined]
        conn.commit()
        conn.close()
        logger.info("Migración de 'Inventario.categoria' ejecutada correctamente")
        return True
    except Exception as e:
        logger.error(f"Error migrando 'Inventario.categoria': {e}")
        return False

def migracion_catalogo_categorias() -> bool:
    """Crea la tabla 'categorias' y sincroniza valores desde Inventario."""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        db_type = db_manager.db_type

        # Crear tabla categorias si no existe y asegurar 'General'
        if db_type == "sqlite":
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS categorias (
                    nombre VARCHAR(50) PRIMARY KEY
                )
                '''
            )
            cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES ('General')")
            # Sincronizar desde Inventario
            cursor.execute(
                "INSERT OR IGNORE INTO categorias (nombre) "
                "SELECT DISTINCT COALESCE(NULLIF(TRIM(categoria), ''), 'General') FROM Inventario"
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS categorias (
                    nombre VARCHAR(50) PRIMARY KEY
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            cursor.execute("INSERT IGNORE INTO categorias (nombre) VALUES ('General')")
            # Sincronizar desde Inventario
            cursor.execute(
                "INSERT IGNORE INTO categorias (nombre) "
                "SELECT DISTINCT IFNULL(NULLIF(TRIM(categoria), ''), 'General') FROM Inventario"
            )

        conn.commit()
        conn.close()
        logger.info("Catálogo 'categorias' creado/sincronizado correctamente")
        return True
    except Exception as e:
        logger.error(f"Error en migracion_catalogo_categorias: {e}")
        return False