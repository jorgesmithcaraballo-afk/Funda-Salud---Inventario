"""
Servicio de aplicación: autenticación de usuarios.

Encapsula la lógica de autenticación para que las vistas (Tkinter) permanezcan limpias.
"""

from __future__ import annotations

from typing import Optional, Tuple, Dict, Any
import hashlib
import os
import logging

from db.crud.personal_crud_service import PersonalCRUD


logger = logging.getLogger(__name__)


class LoginService:
    """Servicio para autenticación de usuarios."""

    @staticmethod
    def hash_password(password: str, iterations: int = 100_000) -> str:
        """Genera hash seguro PBKDF2-HMAC-SHA256 con salt aleatoria.
        Formato: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
        """
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

    @staticmethod
    def verify_password(password: str, stored: Optional[str]) -> bool:
        """Verifica contraseña con soporte de hash y modo legacy (texto plano)."""
        try:
            if stored and "$" in stored:
                algo, iter_s, salt_hex, hash_hex = stored.split("$", 3)
                if algo != "pbkdf2_sha256":
                    return False
                iterations = int(iter_s)
                salt = bytes.fromhex(salt_hex)
                expected = bytes.fromhex(hash_hex)
                dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
                return dk == expected
            return (stored or "") == password
        except Exception:
            return False

    @staticmethod
    def authenticate(username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Autentica usuario por nombre.

        Retorna (ok, user_row, error_message).
        Si ok=True, user_row contiene al menos id, nombre, tipo.
        """
        try:
            # Normalizar a minúsculas para login case-insensitive
            username_norm = (username or "").strip().lower()
            row = None
            # Intento 1: buscar por nombre normalizado (si la capa CRUD o la DB no es case-insensitive, podría no encontrar)
            try:
                row = PersonalCRUD.get_by_nombre(username_norm)
            except Exception:
                row = None
            # Intento 2: buscar por nombre tal cual ingresó
            if not row:
                row = PersonalCRUD.get_by_nombre(username)
            if not row:
                return False, None, None

            # Validar que coincida el nombre de usuario case-insensitive
            try:
                db_name = (row.get("nombre") or "").strip().lower()
                if db_name != username_norm:
                    return False, None, None
            except Exception:
                pass

            stored = row.get("contrasena")
            ok = LoginService.verify_password(password, stored)

            # Si fue legacy y coincide, actualizar a hash seguro (best-effort)
            if ok and (stored is None or "$" not in stored):
                try:
                    new_hash = LoginService.hash_password(password)
                    PersonalCRUD.update(user_id=row.get("id"), contrasena=new_hash)
                except Exception as _:
                    # No interrumpir login por fallo de actualización
                    pass

            return ok, row if ok else None, None
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return False, None, str(e)

