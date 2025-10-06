"""
Script para agregar las columnas faltantes en las tablas de movimientos de SQLite
"""
import sqlite3
import sys

DB_PATH = "database/sistema_inventario.db"

def fix_movement_tables():
    """Agregar columnas cantidad y costo a las tablas de movimientos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['existencia_inicial', 'entradas', 'salidas', 'existencia_final']
    
    for table in tables:
        print(f"\n📋 Procesando tabla: {table}")
        
        # Verificar columnas actuales
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"   Columnas actuales: {columns}")
        
        # Agregar columna 'cantidad' si no existe
        if 'cantidad' not in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN cantidad INTEGER DEFAULT 0")
                print(f"   ✅ Agregada columna 'cantidad'")
            except Exception as e:
                print(f"   ⚠️  Error agregando 'cantidad': {e}")
        else:
            print(f"   ℹ️  Columna 'cantidad' ya existe")
        
        # Agregar columna 'costo' si no existe
        if 'costo' not in columns:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN costo DECIMAL(10,2) DEFAULT 0")
                print(f"   ✅ Agregada columna 'costo'")
            except Exception as e:
                print(f"   ⚠️  Error agregando 'costo': {e}")
        else:
            print(f"   ℹ️  Columna 'costo' ya existe")
    
    conn.commit()
    
    # Verificar estructura final
    print("\n" + "="*60)
    print("ESTRUCTURA FINAL")
    print("="*60)
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        print(f"\n{table}:")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n✅ Estructura de tablas corregida")

if __name__ == "__main__":
    print("="*60)
    print("CORRECCIÓN DE ESTRUCTURA DE TABLAS SQLite")
    print("="*60)
    
    try:
        fix_movement_tables()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
