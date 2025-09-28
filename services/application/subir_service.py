"""
Servicio de aplicación para la vista Subir.

Reutiliza FiltroService para evitar duplicación y expone una API específica para SubirView.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from services.application.filtro_service import FiltroService
from db.crud.inventario_crud_service import InventarioCRUD
from db.crud.existencia_inicial_crud_service import ExistenciaInicialCRUD
from db.crud.entradas_crud_service import EntradasCRUD
from db.crud.salidas_crud_service import SalidasCRUD
from db.crud.existencia_final_crud_service import ExistenciaFinalCRUD


class SubirService:
    @staticmethod
    def get_categories() -> List[str]:
        return FiltroService.get_categories()

    @staticmethod
    def load_inventario_codes_map() -> Tuple[
        List[str], List[str], Dict[str, Dict[str, Any]], Dict[str, str], Dict[str, str]
    ]:
        return FiltroService.load_inventario_codes_map()

    @staticmethod
    def fetch_inventory_by_code(code: str) -> Optional[Dict[str, Any]]:
        return FiltroService.fetch_inventory_by_code(code)

    @staticmethod
    def save_inventory_and_movement(
        code: str,
        descripcion: str,
        costo_unitario: float,
        categoria_catalogo: str,
        categoria_movimiento: str,
        cantidad: Optional[float],
        costo_mov: Optional[float],
    ) -> bool:
        return FiltroService.save_inventory_and_movement(
            code=code,
            descripcion=descripcion,
            costo_unitario=costo_unitario,
            categoria_catalogo=categoria_catalogo,
            categoria_movimiento=categoria_movimiento,
            cantidad=cantidad,
            costo_mov=costo_mov,
        )

    @staticmethod
    def get_movement_by_category(code_or_id: str, categoria_movimiento: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
        """Obtiene (cantidad, costo) desde la tabla correspondiente a la categoría seleccionada.

        Acepta 'code_or_id' como código de negocio (Inventario.codigo) o como id numérico (PK).
        Resuelve el inventario_id de forma robusta antes de consultar la tabla de movimientos.
        Retorna None si no existe registro.
        """
        crud_map = {
            "E. Inicial": ExistenciaInicialCRUD,
            "Entradas": EntradasCRUD,
            "Salidas": SalidasCRUD,
        }
        crud = crud_map.get(categoria_movimiento)
        if not crud:
            return None
        inv_id = None
        # Resolver por código de negocio primero
        try:
            inv = InventarioCRUD.get_by_codigo(str(code_or_id))
            if inv and inv.get("id") is not None:
                inv_id = int(inv["id"])  # type: ignore[arg-type]
        except Exception:
            inv_id = None
        # Fallback: si no se obtuvo por código, intentar interpretar como id
        if inv_id is None:
            try:
                inv_id = int(code_or_id)
            except Exception:
                inv_id = None
        if inv_id is None:
            return None
        row = crud.get_by_inventario_id(inv_id)
        if not row:
            return None
        return row.get("cantidad"), row.get("costo")
