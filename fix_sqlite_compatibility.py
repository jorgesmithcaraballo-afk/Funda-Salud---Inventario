"""
Script para corregir automáticamente la compatibilidad con SQLite
Reemplaza cursor(dictionary=True) por el helper _get_cursor()
"""
import re

def fix_inventory_queries():
    """Corregir services/domain/inventory_queries.py"""
    file_path = "services/domain/inventory_queries.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar métodos que usan cursor(dictionary=True)
    pattern = r'(conn = obtener_conexion\(\)\s+)cursor = conn\.cursor\(dictionary=True\)'
    
    # Reemplazar con el helper
    replacement = r'\1db_type = get_database_type()\n        cursor = InventoryQueries._get_cursor(conn)'
    
    content = re.sub(pattern, replacement, content)
    
    # Patrón para el return de datos
    pattern_return = r'(\s+)(datos = cursor\.fetchall\(\)\s+cursor\.close\(\)\s+conn\.close\(\)\s+return datos)'
    
    replacement_return = r'\1rows = cursor.fetchall()\n\1cursor.close()\n\1conn.close()\n\1\n\1# Convert rows to dictionaries\n\1if db_type == "sqlite":\n\1    return [dict(row) for row in rows]\n\1else:\n\1    return rows'
    
    content = re.sub(pattern_return, replacement_return, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Corregido: {file_path}")

if __name__ == "__main__":
    fix_inventory_queries()
    print("\n✅ Correcciones completadas")
