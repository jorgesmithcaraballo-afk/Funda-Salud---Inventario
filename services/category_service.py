"""
CategoryService: centralized access to categories for all views.
- Source of truth: table `categorias` (catalog managed in Configuración)
- Always returns a normalized, unique, sorted list; falls back to ['General'] on error/empty.
"""
from __future__ import annotations

from typing import List

from db_utils import QueryExecutor


class CategoryService:
    @staticmethod
    def get_all() -> List[str]:
        """Return list of categories from catalog table.
        - Never raises: on DB errors returns at least ['General'].
        """
        try:
            # Ensure table exists and has 'General'
            try:
                QueryExecutor.execute_query(
                    "CREATE TABLE IF NOT EXISTS categorias (nombre VARCHAR(50) PRIMARY KEY)",
                    fetch_one=False,
                    fetch_all=False,
                )
                QueryExecutor.execute_query(
                    "INSERT IGNORE INTO categorias (nombre) VALUES ('General')",
                    fetch_one=False,
                    fetch_all=False,
                )
            except Exception:
                # Ignore creation issues; fallback below will handle
                pass
            rows = QueryExecutor.execute_query(
                "SELECT nombre FROM categorias ORDER BY nombre ASC",
                fetch_all=True,
            ) or []
            result = []
            for r in rows:
                name = (r.get("nombre") if isinstance(r, dict) else r[0]) if r else None
                if name and name.strip():
                    result.append(name.strip())
            return result or ["General"]
        except Exception:
            return ["General"]
