"""
Servicio de aplicación para Configuración (Usuarios y Categorías).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import hashlib
import os

from database.personal_crud_service import PersonalCRUD
from services.domain.category_service import CategoryService


class ConfiguracionService:
    # ------------------ Usuarios ------------------
    @staticmethod
    def hash_password(password: str, iterations: int = 100_000) -> str:
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

    @staticmethod
    def list_users() -> List[Dict[str, Any]]:
        return PersonalCRUD.list_all()

    @staticmethod
    def add_user(nombre: str, apellido: str, contrasena: str, tipo: str = "user") -> bool:
        hashed = ConfiguracionService.hash_password(contrasena)
        affected = PersonalCRUD.create(nombre=nombre, apellido=apellido, contrasena=hashed, tiempo=None, tipo=tipo)
        return affected > 0

    @staticmethod
    def update_user(user_id: int, nombre: str, apellido: str, tipo: str, nueva_contra: Optional[str] = None) -> bool:
        if nueva_contra:
            hashed = ConfiguracionService.hash_password(nueva_contra)
            affected = PersonalCRUD.update(user_id=user_id, nombre=nombre, apellido=apellido, tipo=tipo, contrasena=hashed)
        else:
            affected = PersonalCRUD.update(user_id=user_id, nombre=nombre, apellido=apellido, tipo=tipo)
        return affected >= 0

    @staticmethod
    def delete_user(user_id: int, nombre: str, tipo: str) -> bool:
        # Proteger admin principal 'naila'
        if (tipo or "user").strip().lower() == "admin" and (nombre or "").strip().lower() == "naila":
            return False
        affected = PersonalCRUD.delete(user_id)
        return affected > 0

    # ------------------ Categorías ------------------
    @staticmethod
    def ensure_categories_table() -> None:
        # Delegar en CategoryService.get_all() que asegura la tabla
        CategoryService.get_all()

    @staticmethod
    def list_categories() -> List[str]:
        return CategoryService.get_all()

    @staticmethod
    def add_category(nombre: str) -> bool:
        return CategoryService.add(nombre)

    @staticmethod
    def rename_category(old_name: str, new_name: str) -> bool:
        if old_name.strip().lower() == "general":
            return False
        return CategoryService.rename(old_name, new_name)

    @staticmethod
    def delete_category(name: str) -> bool:
        if name.strip().lower() == "general":
            return False
        return CategoryService.delete(name)

