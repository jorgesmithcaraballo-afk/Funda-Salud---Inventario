"""
Servicio de aplicación: lógica de negocio para vistas de Filtro y Subir.

Centraliza acceso a datos (vía CRUDs y QueryExecutor) y utilidades como exportación a Excel.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from database.inventario_crud_service import InventarioCRUD
from database.existencia_inicial_crud_service import ExistenciaInicialCRUD
from database.entradas_crud_service import EntradasCRUD
from database.salidas_crud_service import SalidasCRUD
from database.existencia_final_crud_service import ExistenciaFinalCRUD
from services.domain.inventory_queries import InventoryQueries
from services.domain.category_service import CategoryService


class FiltroService:
    """Servicios de datos para filtros, búsquedas y edición de inventario."""

    # ------------------ Categorías ------------------
    @staticmethod
    def get_categories() -> List[str]:
        """Obtiene categorías desde servicio de dominio (catálogo)."""
        return CategoryService.get_all() or ["General"]

    # ------------------ Inventario (lecturas) ------------------
    @staticmethod
    def get_base_inventory_data() -> List[Dict[str, Any]]:
        """Datos base usados por la vista Filtro (unificados desde InventoryQueries)."""
        return InventoryQueries.get_base_inventory_data()

    @staticmethod
    def load_inventario_codes_map() -> Tuple[
        List[str], List[str], Dict[str, Dict[str, Any]], Dict[str, str], Dict[str, str]
    ]:
        """Carga códigos/labels/mapas del inventario para autocompletado en Subir.

        Devuelve:
        - lista códigos (values)
        - lista descripciones label (values)
        - mapa: code -> {descripcion_insumo, costo_unitario, categoria}
        - mapa: desc_label -> code
        - mapa: code -> desc_label
        """
        rows = InventarioCRUD.list_all(limit=10000, offset=0) or []

        inventario_map: Dict[str, Dict[str, Any]] = {}
        desc_label_to_code: Dict[str, str] = {}
        code_to_desc_label: Dict[str, str] = {}
        values: List[str] = []
        desc_values: List[str] = []
        seen_desc: Dict[str, int] = {}
        for row in rows:
            code = str(row.get("id"))
            desc = (row.get("descripcion_insumo") or "")
            cost = row.get("costo_unitario")
            cat = (row.get("categoria") or "General")
            inventario_map[code] = {
                "descripcion_insumo": desc,
                "costo_unitario": cost if (cost is not None) else "",
                "categoria": cat,
            }
            values.append(code)
            base_desc = desc.strip()
            if not base_desc:
                label = f"(sin descripción) (ID:{code})"
            else:
                if base_desc in seen_desc:
                    seen_desc[base_desc] += 1
                    label = f"{base_desc} (ID:{code})"
                else:
                    seen_desc[base_desc] = 1
                    label = base_desc
            desc_label_to_code[label] = code
            code_to_desc_label[code] = label
            desc_values.append(label)
        return values, desc_values, inventario_map, desc_label_to_code, code_to_desc_label

    @staticmethod
    def fetch_inventory_by_code(code: str) -> Optional[Dict[str, Any]]:
        row = InventarioCRUD.get_by_id(int(code))
        if not row:
            return None
        return {
            "descripcion_insumo": row.get("descripcion_insumo") or "",
            "costo_unitario": row.get("costo_unitario") if row.get("costo_unitario") is not None else "",
            "categoria": row.get("categoria") or "General",
        }

    # ------------------ Inventario (escrituras) ------------------
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
        """Guarda/actualiza Inventario y el movimiento asociado según categoría seleccionada."""
        # Upsert Inventario
        exists = InventarioCRUD.get_by_id(int(code))
        if not exists:
            InventarioCRUD.create(int(code), descripcion, costo_unitario, categoria_catalogo)
        else:
            InventarioCRUD.update(int(code), descripcion_insumo=descripcion, costo_unitario=costo_unitario, categoria=categoria_catalogo)

        # Movimiento
        table_map = {
            "E. Inicial": ExistenciaInicialCRUD,
            "Entradas": EntradasCRUD,
            "Salidas": SalidasCRUD,
            "E. Final": ExistenciaFinalCRUD,
        }
        crud = table_map.get(categoria_movimiento)
        if crud and cantidad is not None and costo_mov is not None:
            # Upsert por inventario_id
            return bool(crud.upsert_by_inventario_id(int(code), float(cantidad), float(costo_mov)))
        return True

    # ------------------ Exportación a Excel ------------------
    @staticmethod
    def export_inventory_to_excel(datos: List[Dict[str, Any]], ruta_archivo: str) -> None:
        import openpyxl
        from openpyxl.styles import Font

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inventario"

        encabezado = [
            "Código",
            "Descripción",
            "E. Inicial Cant",
            "E. Inicial Costo",
            "E. Inicial Monto",
            "Entradas Cant",
            "Entradas Costo",
            "Entradas Monto",
            "Salidas Cant",
            "Salidas Costo",
            "Salidas Monto",
            "E. Final Cant",
            "E. Final Costo",
            "E. Final Monto",
        ]
        ws.append(encabezado)
        for col in ws.iter_cols(min_row=1, max_row=1):
            for cell in col:
                cell.font = Font(bold=True)

        for item in datos:
            codigo = str(item.get("id", ""))
            descripcion = item.get("descripcion_insumo", "")
            costo_unitario = item.get("costo_unitario") or 0
            cant_inicial = item.get("ei_cant") or 0
            costo_inicial = item.get("ei_costo") or 0
            monto_inicial = cant_inicial * costo_inicial
            cant_entrada = item.get("e_cant") or 0
            costo_entrada = item.get("e_costo") or 0
            monto_entrada = cant_entrada * costo_entrada
            cant_salida = item.get("s_cant") or 0
            costo_salida = item.get("s_costo") or 0
            monto_salida = cant_salida * costo_salida
            existencia_final = cant_inicial + cant_entrada - cant_salida
            monto_final = monto_inicial + monto_entrada - monto_salida

            fila = [
                codigo,
                descripcion,
                cant_inicial,
                costo_inicial,
                monto_inicial,
                cant_entrada,
                costo_entrada,
                monto_entrada,
                cant_salida,
                costo_salida,
                monto_salida,
                existencia_final,
                costo_unitario,
                monto_final,
            ]
            ws.append(fila)

        wb.save(ruta_archivo)

