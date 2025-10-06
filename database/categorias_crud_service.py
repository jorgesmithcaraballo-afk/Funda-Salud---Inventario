"""
CRUD para la tabla 'categorias'.

Estructura esperada (MySQL):
- nombre (VARCHAR(50) PRIMARY KEY)

Incluye helpers para asegurar la tabla y sincronizar referencias con Inventario
cuando se renombra o elimina una categoría.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from database.db_utils import QueryExecutor

TABLE_NAME = "categorias"


class CategoriasCRUD:
    """Servicio CRUD para la tabla 'categorias'."""

    @staticmethod
    def ensure_table() -> None:
        QueryExecutor.execute_query(
            "CREATE TABLE IF NOT EXISTS categorias (nombre VARCHAR(50) PRIMARY KEY)",
            fetch_one=False,
            fetch_all=False,
        )
        # Asegurar 'General'
        QueryExecutor.execute_query(
            "INSERT IGNORE INTO categorias (nombre) VALUES ('General')",
            fetch_one=False,
            fetch_all=False,
        )

    # ---- Básicos ----
    @staticmethod
    def list_all() -> List[str]:
        CategoriasCRUD.ensure_table()
        rows = QueryExecutor.execute_query(
            "SELECT nombre FROM categorias ORDER BY nombre ASC",
            fetch_all=True,
        ) or []
        return [r.get("nombre") if isinstance(r, dict) else r[0] for r in rows]

    @staticmethod
    def add(nombre: str) -> int:
        CategoriasCRUD.ensure_table()
        return int(
            QueryExecutor.execute_query(
                "INSERT IGNORE INTO categorias (nombre) VALUES (%s)",
                (nombre,),
                fetch_one=False,
                fetch_all=False,
            )
            or 0
        )

    @staticmethod
    def rename(old_name: str, new_name: str) -> bool:
        if old_name.strip().lower() == "general":
            return False
        CategoriasCRUD.ensure_table()
        # Actualizar catálogo
        QueryExecutor.execute_query(
            "UPDATE categorias SET nombre=%s WHERE nombre=%s",
            (new_name, old_name),
            fetch_one=False,
            fetch_all=False,
        )
        QueryExecutor.execute_query(
            "INSERT IGNORE INTO categorias (nombre) VALUES (%s)",
            (new_name,),
            fetch_one=False,
            fetch_all=False,
        )
        # Sincronizar Inventario
        QueryExecutor.execute_query(
            "UPDATE Inventario SET categoria=%s WHERE categoria=%s",
            (new_name, old_name),
            fetch_one=False,
            fetch_all=False,
        )
        return True

    @staticmethod
    def delete(nombre: str) -> bool:
        if nombre.strip().lower() == "general":
            return False
        CategoriasCRUD.ensure_table()
        # Reasignar referencias a 'General'
        QueryExecutor.execute_query(
            "UPDATE Inventario SET categoria='General' WHERE categoria=%s",
            (nombre,),
            fetch_one=False,
            fetch_all=False,
        )
        affected = QueryExecutor.execute_query(
            "DELETE FROM categorias WHERE nombre=%s",
            (nombre,),
            fetch_one=False,
            fetch_all=False,
        )
        return bool(affected)
