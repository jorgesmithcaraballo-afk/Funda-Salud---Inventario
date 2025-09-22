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
                contrasena VARCHAR(20) NOT NULL
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
                monto_total DECIMAL(10, 2)
            )
        ''')
        
        # Crear tablas hijas
        for tabla in ['existencia_inicial', 'entradas', 'salidas', 'existencia_final']:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {tabla} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventario_id INTEGER,
                    nombre VARCHAR(50),
                    FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
                )
            ''')
        
        # Crear usuario administrador por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM personal WHERE nombre = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO personal (nombre, apellido, tiempo, contrasena) 
                VALUES ('admin', 'sistema', 60, 'admin123')
            ''')
        
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
            
            conn.commit()
        except FileNotFoundError:
            logger.warning("No se encontró estructura_bd.sql, creando estructura básica")
            # Crear estructura básica si no hay archivo SQL
            cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_inventario")
            cursor.execute("USE sistema_inventario")
        
        conn.close()
        logger.info("Estructura MySQL creada correctamente")
    
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
                    INSERT OR REPLACE INTO personal (id, nombre, apellido, tiempo, contrasena)
                    VALUES (?, ?, ?, ?, ?)
                ''', (row['id'], row['nombre'], row['apellido'], row['tiempo'], row['contrasena']))
            
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


def get_database_type():
    """Obtener tipo de base de datos en uso"""
    return db_manager.db_type


def migrar_a_sqlite():
    """Migrar datos a SQLite si es posible"""
    return db_manager.migrate_to_sqlite()