"""
CRUD para la tabla 'existencia_inicial'.

Columnas esperadas:
- id (INT AUTO_INCREMENT, PK)
- inventario_id (INT, FK a Inventario.id)
- cantidad (DECIMAL/INT)
- costo (DECIMAL)
"""

from typing import Any, Dict, List, Optional
from database.db_utils import QueryExecutor


TABLE_NAME = "existencia_inicial"


class ExistenciaInicialCRUD:
    """Servicio CRUD para 'existencia_inicial'."""

    @staticmethod
    def create(inventario_id: int, cantidad: float, costo: float) -> int:
        query = f"INSERT INTO {TABLE_NAME} (inventario_id, cantidad, costo) VALUES (%s, %s, %s)"
        return int(
            QueryExecutor.execute_query(query, (inventario_id, cantidad, costo), fetch_one=False, fetch_all=False)
            or 0
        )

    @staticmethod
    def get_by_id(row_id: int) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} WHERE id = %s"
        return QueryExecutor.execute_query(query, (row_id,), fetch_one=True, fetch_all=False)

    @staticmethod
    def get_by_inventario_id(inventario_id: int) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} WHERE inventario_id = %s LIMIT 1"
        return QueryExecutor.execute_query(query, (inventario_id,), fetch_one=True, fetch_all=False)

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} ORDER BY id ASC LIMIT %s OFFSET %s"
        return QueryExecutor.execute_query(query, (limit, offset), fetch_one=False, fetch_all=True) or []

    @staticmethod
    def update(row_id: int, cantidad: Optional[float] = None, costo: Optional[float] = None) -> int:
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
        params.append(row_id)
        query = f"UPDATE {TABLE_NAME} SET {', '.join(sets)} WHERE id = %s"
        return int(QueryExecutor.execute_query(query, tuple(params), fetch_one=False, fetch_all=False) or 0)

    @staticmethod
    def upsert_by_inventario_id(inventario_id: int, cantidad: float, costo: float) -> bool:
        existing = ExistenciaInicialCRUD.get_by_inventario_id(inventario_id)
        if existing:
            affected = ExistenciaInicialCRUD.update(existing.get("id"), cantidad=cantidad, costo=costo)
            return affected >= 0
        affected = ExistenciaInicialCRUD.create(inventario_id, cantidad, costo)
        return affected > 0

    @staticmethod
    def delete(row_id: int) -> int:
        query = f"DELETE FROM {TABLE_NAME} WHERE id = %s"
        return int(QueryExecutor.execute_query(query, (row_id,), fetch_one=False, fetch_all=False) or 0)

    @staticmethod
    def delete_by_inventario_id(inventario_id: int) -> int:
        query = f"DELETE FROM {TABLE_NAME} WHERE inventario_id = %s"
        return int(QueryExecutor.execute_query(query, (inventario_id,), fetch_one=False, fetch_all=False) or 0)

