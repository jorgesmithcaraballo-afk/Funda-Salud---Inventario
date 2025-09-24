"""
CRUD para la tabla 'entradas'.

Estructura esperada (MySQL):
- id (INT AUTO_INCREMENT, PK)
- inventario_id (INT, FK a Inventario.id)
- cantidad (DECIMAL/INT)
- costo (DECIMAL)

Todas las operaciones usan placeholders estilo MySQL (%s) y db_utils.QueryExecutor
para asegurar manejo correcto de conexiones y errores.
"""

from typing import Any, Dict, List, Optional, Tuple
from db.db_utils import QueryExecutor, DatabaseError


TABLE_NAME = "entradas"


class EntradasCRUD:
    """Servicio CRUD para la tabla 'entradas'."""

    @staticmethod
    def create(inventario_id: int, cantidad: float, costo: float) -> int:
        """Crea un registro en 'entradas' y devuelve filas afectadas (1 si ok)."""
        query = (
            f"INSERT INTO {TABLE_NAME} (inventario_id, cantidad, costo) VALUES (%s, %s, %s)"
        )
        return int(
            QueryExecutor.execute_query(query, (inventario_id, cantidad, costo), fetch_one=False, fetch_all=False)
            or 0
        )

    @staticmethod
    def get_by_id(entrada_id: int) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} WHERE id = %s"
        return QueryExecutor.execute_query(query, (entrada_id,), fetch_one=True, fetch_all=False)

    @staticmethod
    def get_by_inventario_id(inventario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene la fila asociada a un inventario_id (asumiendo 1 a 1)."""
        query = f"SELECT * FROM {TABLE_NAME} WHERE inventario_id = %s LIMIT 1"
        return QueryExecutor.execute_query(query, (inventario_id,), fetch_one=True, fetch_all=False)

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} ORDER BY id ASC LIMIT %s OFFSET %s"
        return QueryExecutor.execute_query(query, (limit, offset), fetch_one=False, fetch_all=True) or []

    @staticmethod
    def update(entrada_id: int, cantidad: Optional[float] = None, costo: Optional[float] = None) -> int:
        """Actualiza campos provistos en una entrada. Devuelve filas afectadas."""
        sets: List[str] = []
        params: List[Any] = []
        if cantidad is not None:
            sets.append("cantidad = %s")
            params.append(cantidad)
        if costo is not None:
            sets.append("costo = %s")
            params.append(costo)
        if not sets:
            return 0
        params.append(entrada_id)
        query = f"UPDATE {TABLE_NAME} SET {', '.join(sets)} WHERE id = %s"
        return int(QueryExecutor.execute_query(query, tuple(params), fetch_one=False, fetch_all=False) or 0)

    @staticmethod
    def upsert_by_inventario_id(inventario_id: int, cantidad: float, costo: float) -> bool:
        """Inserta o actualiza por inventario_id (si existe, actualiza)."""
        try:
            existing = EntradasCRUD.get_by_inventario_id(inventario_id)
            if existing:
                affected = EntradasCRUD.update(existing.get("id"), cantidad=cantidad, costo=costo)
                return affected >= 0
            else:
                affected = EntradasCRUD.create(inventario_id, cantidad, costo)
                return affected > 0
        except DatabaseError:
            raise

    @staticmethod
    def delete(entrada_id: int) -> int:
        query = f"DELETE FROM {TABLE_NAME} WHERE id = %s"
        return int(QueryExecutor.execute_query(query, (entrada_id,), fetch_one=False, fetch_all=False) or 0)

    @staticmethod
    def delete_by_inventario_id(inventario_id: int) -> int:
        query = f"DELETE FROM {TABLE_NAME} WHERE inventario_id = %s"
        return int(QueryExecutor.execute_query(query, (inventario_id,), fetch_one=False, fetch_all=False) or 0)

