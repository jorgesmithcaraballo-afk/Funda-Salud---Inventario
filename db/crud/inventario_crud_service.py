"""
CRUD para la tabla 'Inventario'.

Columnas manejadas (según uso en la app):
- id (INT, PK)
- codigo (VARCHAR, UNIQUE)  # clave de negocio
- descripcion_insumo (VARCHAR)
- costo_unitario (DECIMAL)
- categoria (VARCHAR, DEFAULT 'General')

Otras columnas posibles según tu esquema (tipo, cantidad, monto_total) se dejan opcionales.
"""

from typing import Any, Dict, List, Optional
from db.db_utils import QueryExecutor


TABLE_NAME = "Inventario"


class InventarioCRUD:
    """Servicio CRUD para 'Inventario'."""

    @staticmethod
    def create(id_: int, descripcion_insumo: str, costo_unitario: float, categoria: str = "General") -> int:
        """Inserta un producto en Inventario usando id explícito (legacy). Devuelve filas afectadas."""
        query = (
            f"""
            INSERT INTO {TABLE_NAME} (id, descripcion_insumo, costo_unitario, categoria)
            VALUES (%s, %s, %s, %s)
            """
        )
        return int(
            QueryExecutor.execute_query(query, (id_, descripcion_insumo, costo_unitario, categoria), fetch_one=False, fetch_all=False)
            or 0
        )

    @staticmethod
    def create_with_codigo(codigo: str, descripcion_insumo: str, costo_unitario: float, categoria: str = "General") -> int:
        """Inserta un producto estableciendo 'codigo' como clave de negocio (id autoincremental)."""
        query = (
            f"""
            INSERT INTO {TABLE_NAME} (codigo, descripcion_insumo, costo_unitario, categoria)
            VALUES (%s, %s, %s, %s)
            """
        )
        return int(
            QueryExecutor.execute_query(query, (codigo, descripcion_insumo, costo_unitario, categoria), fetch_one=False, fetch_all=False)
            or 0
        )

    @staticmethod
    def get_by_id(id_: int) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} WHERE id = %s"
        return QueryExecutor.execute_query(query, (id_,), fetch_one=True, fetch_all=False)

    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} WHERE codigo = %s"
        return QueryExecutor.execute_query(query, (codigo,), fetch_one=True, fetch_all=False)

    @staticmethod
    def list_all(limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} ORDER BY codigo ASC, id ASC LIMIT %s OFFSET %s"
        return QueryExecutor.execute_query(query, (limit, offset), fetch_one=False, fetch_all=True) or []

    @staticmethod
    def search_by_text(text: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Búsqueda simple por codigo, id o descripción (LIKE)."""
        like = f"%{text}%"
        query = (
            f"SELECT * FROM {TABLE_NAME} "
            "WHERE codigo LIKE %s OR CAST(id AS CHAR) LIKE %s OR descripcion_insumo LIKE %s "
            "ORDER BY codigo ASC, id ASC LIMIT %s"
        )
        return QueryExecutor.execute_query(query, (like, like, like, limit), fetch_one=False, fetch_all=True) or []

    @staticmethod
    def update(
        id_: int,
        descripcion_insumo: Optional[str] = None,
        costo_unitario: Optional[float] = None,
        categoria: Optional[str] = None,
    ) -> int:
        """Actualiza campos provistos para un item de Inventario."""
        sets: List[str] = []
        params: List[Any] = []
        if descripcion_insumo is not None:
            sets.append("descripcion_insumo = %s")
            params.append(descripcion_insumo)
        if costo_unitario is not None:
            sets.append("costo_unitario = %s")
            params.append(costo_unitario)
        if categoria is not None:
            sets.append("categoria = %s")
            params.append(categoria)
        if not sets:
            return 0
        params.append(id_)
        query = f"UPDATE {TABLE_NAME} SET {', '.join(sets)} WHERE id = %s"
        return int(QueryExecutor.execute_query(query, tuple(params), fetch_one=False, fetch_all=False) or 0)

    @staticmethod
    def update_by_codigo(
        codigo: str,
        descripcion_insumo: Optional[str] = None,
        costo_unitario: Optional[float] = None,
        categoria: Optional[str] = None,
    ) -> int:
        """Actualiza campos usando 'codigo' como clave de negocio."""
        sets: List[str] = []
        params: List[Any] = []
        if descripcion_insumo is not None:
            sets.append("descripcion_insumo = %s")
            params.append(descripcion_insumo)
        if costo_unitario is not None:
            sets.append("costo_unitario = %s")
            params.append(costo_unitario)
        if categoria is not None:
            sets.append("categoria = %s")
            params.append(categoria)
        if not sets:
            return 0
        params.append(codigo)
        query = f"UPDATE {TABLE_NAME} SET {', '.join(sets)} WHERE codigo = %s"
        return int(QueryExecutor.execute_query(query, tuple(params), fetch_one=False, fetch_all=False) or 0)

    @staticmethod
    def delete(id_: int) -> int:
        query = f"DELETE FROM {TABLE_NAME} WHERE id = %s"
        return int(QueryExecutor.execute_query(query, (id_,), fetch_one=False, fetch_all=False) or 0)

