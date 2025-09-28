"""
Servicio de aplicación: lógica de negocio para vistas de Filtro y Subir.

Centraliza acceso a datos (vía CRUDs y QueryExecutor) y utilidades como exportación a Excel.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from db.crud.inventario_crud_service import InventarioCRUD
from db.crud.existencia_inicial_crud_service import ExistenciaInicialCRUD
from db.crud.entradas_crud_service import EntradasCRUD
from db.crud.salidas_crud_service import SalidasCRUD
from db.crud.existencia_final_crud_service import ExistenciaFinalCRUD
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

    # ------------------ Utilidades de filtrado/orden ------------------
    @staticmethod
    def filter_and_sort(
        datos: List[Dict[str, Any]],
        query_text: str,
        category: str,
    ) -> List[Dict[str, Any]]:
        """Aplica filtrado por texto, filtro por categoría y orden.

        No cambia la lógica existente en la vista: divide por ';', busca en 'codigo' o 'id' y 'descripcion_insumo',
        filtra por categoría (excepto 'Todas') y ordena por 'id' ascendente cuando es posible.
        """
        try:
            q = (query_text or "").strip().lower()
            terminos = [t.strip() for t in q.split(";") if t.strip()]
            if terminos:
                tmp: List[Dict[str, Any]] = []
                for item in datos:
                    cod = str(item.get("codigo") or item.get("id") or "")
                    cadena = f"{cod} {item.get('descripcion_insumo', '')}".lower()
                    if any(termino in cadena for termino in terminos):
                        tmp.append(item)
                datos = tmp
            if category and category.lower() != "todas":
                datos = [it for it in datos if (it.get("categoria") or "General") == category]
            try:
                datos.sort(key=lambda r: r.get("id") or 0)
            except Exception:
                pass
            return datos
        except Exception:
            return datos or []

    @staticmethod
    def get_filtered_inventory(query_text: str, category: str) -> List[Dict[str, Any]]:
        """Obtiene datos base y aplica filtrado/ordenamiento centralizado."""
        try:
            base = FiltroService.get_base_inventory_data() or []
            return FiltroService.filter_and_sort(base, query_text, category)
        except Exception:
            return []

    @staticmethod
    def prepare_export_data() -> List[Dict[str, Any]]:
        """Devuelve los datos a exportar. Mantiene compatibilidad con exportación actual."""
        try:
            return FiltroService.get_base_inventory_data() or []
        except Exception:
            return []

    # ------------------ Utilidades de paginación/render por lotes ------------------
    @staticmethod
    def paginate(
        datos: List[Dict[str, Any]], start_index: int, batch_size: int
    ) -> Tuple[List[Dict[str, Any]], int, bool]:
        """Devuelve un lote de datos y el próximo índice.

        Retorna: (batch, next_index, has_more)
        - batch: sublista desde start_index con tamaño hasta batch_size
        - next_index: índice siguiente para continuar
        - has_more: True si quedan elementos por procesar
        """
        try:
            n = len(datos) if datos is not None else 0
            if n == 0 or start_index >= n or batch_size <= 0:
                return [], start_index, False
            end = min(start_index + batch_size, n)
            batch = datos[start_index:end]
            next_index = end
            has_more = end < n
            return batch, next_index, has_more
        except Exception:
            return [], start_index, False

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
            # Prefer business key 'codigo'; fallback to numeric id for legacy rows
            code = str(row.get("codigo") or row.get("id"))
            desc = (row.get("descripcion_insumo") or "")
            cost = row.get("costo_unitario")
            cat = (row.get("categoria") or "General")
            # This is the correct structure, as used by SubirView
            inventario_map[code] = {
                "id": row.get("id"), # Pass the original ID for future queries
                "descripcion_insumo": desc,
                "costo_unitario": cost if (cost is not None) else "",
                "categoria": cat,
            }
            values.append(code)
            base_desc = desc.strip()
            if not base_desc:
                label = f"(sin descripción) (COD:{code})"
            else:
                if base_desc in seen_desc:
                    seen_desc[base_desc] += 1
                    label = f"{base_desc} (COD:{code})"
                else:
                    seen_desc[base_desc] = 1
                    label = base_desc
            desc_label_to_code[label] = code
            code_to_desc_label[code] = label
            desc_values.append(label)
        # Sort descriptions alphabetically (case-insensitive)
        desc_values.sort(key=str.lower)

        # Sort codes using natural sorting (handles numbers correctly)
        import re
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]
        values.sort(key=natural_sort_key)

        # The returned maps should not be lowercased here, the view will handle it.
        # The view is responsible for lowercasing the keys for its own lookup map.
        return values, desc_values, inventario_map, desc_label_to_code, code_to_desc_label

    @staticmethod
    def fetch_inventory_by_code(code: str) -> Optional[Dict[str, Any]]:
        # Try by business code first; fallback to id if numeric
        row = InventarioCRUD.get_by_codigo(code)
        if not row:
            try:
                row = InventarioCRUD.get_by_id(int(code))
            except Exception:
                row = None
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
        # Upsert Inventario usando 'codigo' (clave de negocio)
        exists = InventarioCRUD.get_by_codigo(code)
        if not exists:
            InventarioCRUD.create_with_codigo(code, descripcion, costo_unitario, categoria_catalogo)
            # Obtener fila recién creada para resolver id
            exists = InventarioCRUD.get_by_codigo(code)
        else:
            InventarioCRUD.update_by_codigo(code, descripcion_insumo=descripcion, costo_unitario=costo_unitario, categoria=categoria_catalogo)

        # Movimiento: requiere inventario_id (id PK)
        table_map = {
            "E. Inicial": ExistenciaInicialCRUD,
            "Entradas": EntradasCRUD,
            "Salidas": SalidasCRUD,
        }
        crud = table_map.get(categoria_movimiento)
        if crud and cantidad is not None and costo_mov is not None:
            try:
                inv_id = int(exists.get("id")) if exists else int(code)  # fallback para compatibilidad
            except Exception:
                inv_id = None
            if inv_id is None:
                return False
            # Upsert por inventario_id
            return bool(crud.upsert_by_inventario_id(inv_id, float(cantidad), float(costo_mov)))
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
            # Preferir 'codigo' si está disponible en el dataset
            codigo = str(item.get("codigo") or item.get("id", ""))
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

