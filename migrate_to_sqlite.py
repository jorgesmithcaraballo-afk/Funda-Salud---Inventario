"""
Script de migración de datos de MySQL a SQLite
Migra todas las tablas y datos del sistema de inventario
"""
import mysql.connector
import sqlite3
import os
import sys
from pathlib import Path
from typing import List, Tuple, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Importar configuraciones
from config import db_config, app_config


class DatabaseMigrator:
    """Migra datos de MySQL a SQLite"""
    
    def __init__(self):
        self.mysql_conn: Optional[mysql.connector.MySQLConnection] = None
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        self.sqlite_path = app_config.get_database_path()
        
    def connect_mysql(self) -> bool:
        """Conectar a MySQL"""
        try:
            self.mysql_conn = mysql.connector.connect(
                host=db_config.MYSQL_HOST,
                user=db_config.MYSQL_USER,
                password=db_config.MYSQL_PASSWORD,
                database=db_config.MYSQL_DATABASE
            )
            logger.info("✅ Conectado a MySQL exitosamente")
            return True
        except mysql.connector.Error as e:
            logger.error(f"❌ Error conectando a MySQL: {e}")
            return False
    
    def connect_sqlite(self) -> bool:
        """Conectar a SQLite"""
        try:
            # Asegurar que el directorio existe
            Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info(f"✅ Conectado a SQLite: {self.sqlite_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"❌ Error conectando a SQLite: {e}")
            return False
    
    def create_sqlite_structure(self) -> bool:
        """Crear estructura de tablas en SQLite"""
        try:
            cursor = self.sqlite_conn.cursor()
            
            logger.info("📋 Creando estructura de tablas en SQLite...")
            
            # Tabla personal
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
            
            # Tabla Inventario (padre)
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
            
            # Tabla existencia_inicial
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS existencia_inicial (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventario_id INTEGER,
                    nombre VARCHAR(50),
                    cantidad INTEGER,
                    costo DECIMAL(10, 2),
                    FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
                )
            ''')
            
            # Tabla entradas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entradas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventario_id INTEGER,
                    nombre VARCHAR(50),
                    cantidad INTEGER,
                    costo DECIMAL(10, 2),
                    FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
                )
            ''')
            
            # Tabla salidas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS salidas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventario_id INTEGER,
                    nombre VARCHAR(50),
                    cantidad INTEGER,
                    costo DECIMAL(10, 2),
                    FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
                )
            ''')
            
            # Tabla existencia_final
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS existencia_final (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventario_id INTEGER,
                    nombre VARCHAR(50),
                    cantidad INTEGER,
                    costo DECIMAL(10, 2),
                    FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
                )
            ''')
            
            # Tabla categorias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categorias (
                    nombre VARCHAR(50) PRIMARY KEY
                )
            ''')
            
            # Insertar categoría por defecto
            cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES ('General')")
            
            self.sqlite_conn.commit()
            logger.info("✅ Estructura de tablas creada exitosamente")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Error creando estructura SQLite: {e}")
            return False
    
    def migrate_table(self, table_name: str, columns: List[str]) -> Tuple[int, int]:
        """
        Migrar una tabla específica de MySQL a SQLite
        
        Args:
            table_name: Nombre de la tabla
            columns: Lista de columnas a migrar (sin 'id' si es auto-increment)
        
        Returns:
            Tuple[int, int]: (registros leídos, registros insertados)
        """
        try:
            mysql_cursor = self.mysql_conn.cursor(dictionary=True)
            sqlite_cursor = self.sqlite_conn.cursor()
            
            # Leer datos de MySQL
            mysql_cursor.execute(f"SELECT * FROM {table_name}")
            rows = mysql_cursor.fetchall()
            
            if not rows:
                logger.info(f"⚠️  Tabla '{table_name}' está vacía, omitiendo...")
                return (0, 0)
            
            logger.info(f"📊 Migrando tabla '{table_name}': {len(rows)} registros encontrados")
            
            # Insertar en SQLite
            inserted = 0
            for row in rows:
                try:
                    # Construir query de inserción
                    cols = ', '.join(columns)
                    placeholders = ', '.join(['?' for _ in columns])
                    
                    # Convertir Decimal a float para SQLite
                    values = []
                    for col in columns:
                        val = row[col]
                        # Convertir Decimal a float
                        if hasattr(val, '__class__') and val.__class__.__name__ == 'Decimal':
                            val = float(val)
                        values.append(val)
                    values = tuple(values)
                    
                    query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
                    sqlite_cursor.execute(query, values)
                    inserted += 1
                    
                except sqlite3.Error as e:
                    logger.warning(f"⚠️  Error insertando registro en '{table_name}': {e}")
                    continue
            
            self.sqlite_conn.commit()
            logger.info(f"✅ Tabla '{table_name}': {inserted}/{len(rows)} registros migrados")
            return (len(rows), inserted)
            
        except mysql.connector.Error as e:
            logger.error(f"❌ Error leyendo de MySQL tabla '{table_name}': {e}")
            return (0, 0)
        except sqlite3.Error as e:
            logger.error(f"❌ Error escribiendo en SQLite tabla '{table_name}': {e}")
            return (0, 0)
    
    def migrate_all_data(self) -> bool:
        """Migrar todos los datos de todas las tablas"""
        try:
            logger.info("🚀 Iniciando migración de datos...")
            
            total_read = 0
            total_inserted = 0
            
            # Migrar tabla personal
            read, inserted = self.migrate_table(
                'personal',
                ['nombre', 'apellido', 'tiempo', 'contrasena', 'tipo']
            )
            total_read += read
            total_inserted += inserted
            
            # Migrar tabla Inventario
            read, inserted = self.migrate_table(
                'Inventario',
                ['descripcion_insumo', 'tipo', 'cantidad', 'costo_unitario', 'monto_total', 'categoria']
            )
            total_read += read
            total_inserted += inserted
            
            # Migrar tabla existencia_inicial
            read, inserted = self.migrate_table(
                'existencia_inicial',
                ['inventario_id', 'nombre', 'cantidad', 'costo']
            )
            total_read += read
            total_inserted += inserted
            
            # Migrar tabla entradas
            read, inserted = self.migrate_table(
                'entradas',
                ['inventario_id', 'nombre', 'cantidad', 'costo']
            )
            total_read += read
            total_inserted += inserted
            
            # Migrar tabla salidas
            read, inserted = self.migrate_table(
                'salidas',
                ['inventario_id', 'nombre', 'cantidad', 'costo']
            )
            total_read += read
            total_inserted += inserted
            
            # Migrar tabla existencia_final
            read, inserted = self.migrate_table(
                'existencia_final',
                ['inventario_id', 'nombre', 'cantidad', 'costo']
            )
            total_read += read
            total_inserted += inserted
            
            # Migrar categorías si existe la tabla
            try:
                read, inserted = self.migrate_table(
                    'categorias',
                    ['nombre']
                )
                total_read += read
                total_inserted += inserted
            except:
                logger.info("⚠️  Tabla 'categorias' no existe en MySQL, omitiendo...")
            
            logger.info("=" * 60)
            logger.info(f"✅ MIGRACIÓN COMPLETADA")
            logger.info(f"📊 Total registros leídos: {total_read}")
            logger.info(f"📊 Total registros insertados: {total_inserted}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante migración: {e}")
            return False
    
    def verify_migration(self) -> bool:
        """Verificar que la migración fue exitosa comparando conteos"""
        try:
            logger.info("🔍 Verificando migración...")
            
            mysql_cursor = self.mysql_conn.cursor()
            sqlite_cursor = self.sqlite_conn.cursor()
            
            tables = ['personal', 'Inventario', 'existencia_inicial', 'entradas', 'salidas', 'existencia_final']
            
            all_match = True
            for table in tables:
                # Contar en MySQL
                mysql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                mysql_count = mysql_cursor.fetchone()[0]
                
                # Contar en SQLite
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                match = "✅" if mysql_count == sqlite_count else "❌"
                logger.info(f"{match} {table}: MySQL={mysql_count}, SQLite={sqlite_count}")
                
                if mysql_count != sqlite_count:
                    all_match = False
            
            if all_match:
                logger.info("✅ Verificación exitosa: todos los registros coinciden")
            else:
                logger.warning("⚠️  Algunos registros no coinciden, revisar logs")
            
            return all_match
            
        except Exception as e:
            logger.error(f"❌ Error verificando migración: {e}")
            return False
    
    def close_connections(self):
        """Cerrar todas las conexiones"""
        if self.mysql_conn:
            self.mysql_conn.close()
            logger.info("🔌 Conexión MySQL cerrada")
        
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.info("🔌 Conexión SQLite cerrada")
    
    def run_migration(self) -> bool:
        """Ejecutar migración completa"""
        try:
            logger.info("=" * 60)
            logger.info("🔄 MIGRACIÓN DE MYSQL A SQLITE")
            logger.info("=" * 60)
            
            # Conectar a MySQL
            if not self.connect_mysql():
                return False
            
            # Conectar a SQLite
            if not self.connect_sqlite():
                return False
            
            # Crear estructura
            if not self.create_sqlite_structure():
                return False
            
            # Migrar datos
            if not self.migrate_all_data():
                return False
            
            # Verificar
            self.verify_migration()
            
            logger.info("=" * 60)
            logger.info(f"✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            logger.info(f"📁 Base de datos SQLite: {self.sqlite_path}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error fatal durante migración: {e}")
            return False
        finally:
            self.close_connections()


def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("🔄 SCRIPT DE MIGRACIÓN MYSQL → SQLITE")
    print("Sistema de Inventario - Fundación Salud")
    print("=" * 60 + "\n")
    
    # Confirmar con usuario
    response = input("¿Deseas continuar con la migración? (s/n): ").lower().strip()
    if response not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Migración cancelada por el usuario")
        return
    
    # Ejecutar migración
    migrator = DatabaseMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n✅ ¡Migración completada exitosamente!")
        print(f"📁 Tu base de datos SQLite está en: {migrator.sqlite_path}")
        print("\n💡 Siguiente paso: Actualizar conexion.py para usar SQLite")
    else:
        print("\n❌ La migración falló. Revisa los errores arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
