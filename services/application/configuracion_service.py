"""
Servicio de aplicación para Configuración (Usuarios y Categorías).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import hashlib
import os

from db.crud.personal_crud_service import PersonalCRUD
from services.domain.category_service import CategoryService
from services.application.filtro_service import FiltroService
from db.crud.inventario_crud_service import InventarioCRUD
from db.crud.existencia_inicial_crud_service import ExistenciaInicialCRUD
from db.crud.entradas_crud_service import EntradasCRUD
from db.crud.salidas_crud_service import SalidasCRUD
from db.crud.existencia_final_crud_service import ExistenciaFinalCRUD


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

    # ------------------ Inventario ------------------
    @staticmethod
    def load_inventario_codes_map() -> Tuple[
        List[str], List[str], Dict[str, Dict[str, Any]], Dict[str, str], Dict[str, str]
    ]:
        """Carga los datos del inventario para los comboboxes de selección."""
        return FiltroService.load_inventario_codes_map()

    @staticmethod
    def get_product_history(product_id: int) -> Dict[str, Any]:
        """Recopila toda la información histórica de un producto."""
        history = {
            "inventario": InventarioCRUD.get_by_id(product_id),
            "existencia_inicial": ExistenciaInicialCRUD.get_by_inventario_id(product_id),
            "entradas": EntradasCRUD.get_by_inventario_id(product_id),
            "salidas": SalidasCRUD.get_by_inventario_id(product_id),
            "existencia_final": ExistenciaFinalCRUD.get_by_inventario_id(product_id),
        }
        return history

    @staticmethod
    def delete_product_full(product_id: int) -> bool:
        """Elimina un producto y todos sus registros asociados."""
        try:
            # Delete associated records first to avoid foreign key constraint errors
            ExistenciaInicialCRUD.delete_by_inventario_id(product_id)
            EntradasCRUD.delete_by_inventario_id(product_id)
            SalidasCRUD.delete_by_inventario_id(product_id)
            ExistenciaFinalCRUD.delete_by_inventario_id(product_id)

            # Finally, delete the main product record
            affected_rows = InventarioCRUD.delete(product_id)
            
            return affected_rows > 0
        except Exception as e:
            # In a real-world scenario, you would log this error
            print(f"Error during full product deletion: {e}")
            # Consider using transactions to roll back if any step fails
            return False

