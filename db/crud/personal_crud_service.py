"""
CRUD para la tabla 'personal'.

Columnas manejadas (según uso en la app):
- id (INT AUTO_INCREMENT, PK)
- nombre (VARCHAR)
- apellido (VARCHAR)
- tiempo (INT, NULLABLE)
- contrasena (VARCHAR)
- tipo (VARCHAR, DEFAULT 'user')
"""

from typing import Any, Dict, List, Optional
import os as _os_sys
import sys as _sys
_ROOT = _os_sys.path.dirname(_os_sys.path.dirname(_os_sys.path.dirname(__file__)))
if _ROOT not in _sys.path:
    _sys.path.insert(0, _ROOT)
from db.db_utils import QueryExecutor


TABLE_NAME = "personal"


class PersonalCRUD:
    """Servicio CRUD para 'personal'."""

    @staticmethod
    def create(
        nombre: str,
        apellido: str,
        contrasena: str,
        tiempo: Optional[int] = None,
        tipo: str = "user",
    ) -> int:
        query = (
            f"""
            INSERT INTO {TABLE_NAME} (nombre, apellido, tiempo, contrasena, tipo)
            VALUES (%s, %s, %s, %s, %s)
            """
        )
        return int(
            QueryExecutor.execute_query(query, (nombre, apellido, tiempo, contrasena, tipo), fetch_one=False, fetch_all=False)
            or 0
        )

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} WHERE id = %s"
        return QueryExecutor.execute_query(query, (user_id,), fetch_one=True, fetch_all=False)

    @staticmethod
    def get_by_nombre(nombre: str) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} WHERE nombre = %s LIMIT 1"
        return QueryExecutor.execute_query(query, (nombre,), fetch_one=True, fetch_all=False)

    @staticmethod
    def list_all(limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {TABLE_NAME} ORDER BY id ASC LIMIT %s OFFSET %s"
        return QueryExecutor.execute_query(query, (limit, offset), fetch_one=False, fetch_all=True) or []

    @staticmethod
    def update(
        user_id: int,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        tiempo: Optional[int] = None,
        contrasena: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> int:
        sets: List[str] = []
        params: List[Any] = []
        if nombre is not None:
            sets.append("nombre = %s")
            params.append(nombre)
        if apellido is not None:
            sets.append("apellido = %s")
            params.append(apellido)
        if tiempo is not None:
            sets.append("tiempo = %s")
            params.append(tiempo)
        if contrasena is not None:
            sets.append("contrasena = %s")
            params.append(contrasena)
        if tipo is not None:
            sets.append("tipo = %s")
            params.append(tipo)
        if not sets:
            return 0
        params.append(user_id)
        query = f"UPDATE {TABLE_NAME} SET {', '.join(sets)} WHERE id = %s"
        return int(QueryExecutor.execute_query(query, tuple(params), fetch_one=False, fetch_all=False) or 0)

    @staticmethod
    def delete(user_id: int) -> int:
        query = f"DELETE FROM {TABLE_NAME} WHERE id = %s"
        return int(QueryExecutor.execute_query(query, (user_id,), fetch_one=False, fetch_all=False) or 0)

