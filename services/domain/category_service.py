"""
CategoryService: centralized access to categories for all views.
- Source of truth: table `categorias` (catalog managed in Configuración)
- Always returns a normalized, unique, sorted list; falls back to ['General'] on error/empty.
"""
from __future__ import annotations

from typing import List
from db.crud.categorias_crud_service import CategoriasCRUD


class CategoryService:
    @staticmethod
    def get_all() -> List[str]:
        """Return list of categories from catalog table.
        - Never raises: on DB errors returns at least ['General'].
        """
        try:
            nombres = CategoriasCRUD.list_all()
            return nombres or ["General"]
        except Exception:
            return ["General"]

    @staticmethod
    def add(nombre: str) -> bool:
        try:
            return CategoriasCRUD.add(nombre) > 0
        except Exception:
            return False

    @staticmethod
    def rename(old_name: str, new_name: str) -> bool:
        try:
            return CategoriasCRUD.rename(old_name, new_name)
        except Exception:
            return False

    @staticmethod
    def delete(nombre: str) -> bool:
        try:
            return CategoriasCRUD.delete(nombre)
        except Exception:
            return False
