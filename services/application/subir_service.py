"""
Servicio de aplicación para la vista Subir.

Reutiliza FiltroService para evitar duplicación y expone una API específica para SubirView.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from services.application.filtro_service import FiltroService
from database.existencia_inicial_crud_service import ExistenciaInicialCRUD
from database.entradas_crud_service import EntradasCRUD
from database.salidas_crud_service import SalidasCRUD
from database.existencia_final_crud_service import ExistenciaFinalCRUD


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
    def get_movement_by_category(inventario_id: str, categoria_movimiento: str) -> Optional[Tuple[Optional[float], Optional[float]]]:
        """Obtiene (cantidad, costo) desde la tabla correspondiente a la categoría seleccionada.

        Retorna None si no existe registro.
        """
        crud_map = {
            "E. Inicial": ExistenciaInicialCRUD,
            "Entradas": EntradasCRUD,
            "Salidas": SalidasCRUD,
            "E. Final": ExistenciaFinalCRUD,
        }
        crud = crud_map.get(categoria_movimiento)
        if not crud:
            return None
        row = crud.get_by_inventario_id(int(inventario_id))
        if not row:
            return None
        return row.get("cantidad"), row.get("costo")

