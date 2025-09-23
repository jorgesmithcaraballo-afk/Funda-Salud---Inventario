"""
Centralized SQL Queries for Inventory Management
Contains all inventory-related SQL queries to avoid duplication across modules
"""

from conexion import obtener_conexion
from typing import Dict, List, Optional, Any


class InventoryQueries:
    """Centralized inventory SQL queries service"""
    
    @staticmethod
    def get_base_inventory_data() -> List[Dict]:
        """Base inventory query - returns complete inventory data with all movements"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT 
                i.id,
                i.descripcion_insumo,
                i.categoria,
                i.costo_unitario,
                ei.cantidad AS ei_cant,
                ei.costo AS ei_costo,
                e.cantidad AS e_cant,
                e.costo AS e_costo,
                s.cantidad AS s_cant,
                s.costo AS s_costo
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            """
        )

        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_low_stock_products(threshold: int = 5) -> List[Dict]:
        """Get products with low stock (final existence <= threshold)"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            f"""
            SELECT 
                i.id,
                i.descripcion_insumo as producto,
                i.costo_unitario,
                COALESCE(ei.cantidad, 0) AS cant_inicial,
                COALESCE(e.cantidad, 0) AS cant_entrada,
                COALESCE(s.cantidad, 0) AS cant_salida,
                (COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) AS existencia_final,
                ((COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) * i.costo_unitario) AS monto_final
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            HAVING existencia_final <= {threshold} AND existencia_final > 0
            ORDER BY existencia_final ASC
            LIMIT 10
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_out_of_stock_products() -> List[Dict]:
        """Get products completely out of stock (final existence = 0)"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT 
                i.id,
                i.descripcion_insumo as producto,
                i.costo_unitario,
                (COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) AS existencia_final,
                ((COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) * i.costo_unitario) AS monto_final
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            HAVING existencia_final = 0
            ORDER BY i.descripcion_insumo ASC
            LIMIT 10
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_inventory_value() -> List[Dict]:
        """Get total inventory value and top products by value"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT 
                'TOTAL' as tipo,
                SUM((COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) * i.costo_unitario) AS valor_total
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            HAVING valor_total > 0
            
            UNION ALL
            
            SELECT 
                i.descripcion_insumo as tipo,
                ((COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) * i.costo_unitario) AS valor_total
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            HAVING valor_total > 0
            ORDER BY valor_total DESC
            LIMIT 6
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_top_entries() -> List[Dict]:
        """Get products with highest entries ordered by entry amount"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT 
                i.descripcion_insumo as producto,
                COALESCE(e.cantidad, 0) AS cant_entrada,
                (COALESCE(e.cantidad, 0) * COALESCE(e.costo, 0)) AS monto_entrada
            FROM Inventario i
            LEFT JOIN entradas e ON e.inventario_id = i.id
            WHERE e.cantidad > 0
            ORDER BY monto_entrada DESC
            LIMIT 10
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_top_sales() -> List[Dict]:
        """Get products with highest sales ordered by sales amount"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT 
                i.descripcion_insumo as producto,
                COALESCE(s.cantidad, 0) AS cant_salida,
                (COALESCE(s.cantidad, 0) * COALESCE(s.costo, 0)) AS monto_salida
            FROM Inventario i
            LEFT JOIN salidas s ON s.inventario_id = i.id
            WHERE s.cantidad > 0
            ORDER BY monto_salida DESC
            LIMIT 10
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_total_entries() -> List[Dict]:
        """Get total entry amounts and top entries"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT 
                'TOTAL_ENTRADAS' as tipo,
                SUM(COALESCE(e.cantidad, 0) * COALESCE(e.costo, 0)) AS monto_total_entradas
            FROM entradas e
            WHERE e.cantidad > 0
            
            UNION ALL
            
            SELECT 
                i.descripcion_insumo as tipo,
                (COALESCE(e.cantidad, 0) * COALESCE(e.costo, 0)) AS monto_total_entradas
            FROM Inventario i
            LEFT JOIN entradas e ON e.inventario_id = i.id
            WHERE e.cantidad > 0
            ORDER BY monto_total_entradas DESC
            LIMIT 4
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_total_sales() -> List[Dict]:
        """Get total sales amounts and top sales"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT 
                'TOTAL_SALIDAS' as tipo,
                SUM(COALESCE(s.cantidad, 0) * COALESCE(s.costo, 0)) AS monto_total_salidas
            FROM salidas s
            WHERE s.cantidad > 0
            
            UNION ALL
            
            SELECT 
                i.descripcion_insumo as tipo,
                (COALESCE(s.cantidad, 0) * COALESCE(s.costo, 0)) AS monto_total_salidas
            FROM Inventario i
            LEFT JOIN salidas s ON s.inventario_id = i.id
            WHERE s.cantidad > 0
            ORDER BY monto_total_salidas DESC
            LIMIT 4
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_no_movement_products() -> List[Dict]:
        """Get products with no movements (no entries or sales)"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT 
                i.id,
                i.descripcion_insumo as producto,
                COALESCE(ei.cantidad, 0) AS cant_inicial,
                COALESCE(e.cantidad, 0) AS cant_entrada,
                COALESCE(s.cantidad, 0) AS cant_salida,
                (COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) AS existencia_final
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            WHERE (COALESCE(e.cantidad, 0) = 0 AND COALESCE(s.cantidad, 0) = 0)
            ORDER BY i.descripcion_insumo ASC
            LIMIT 10
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_stock_variation() -> List[Dict]:
        """Get stock variation (difference between final and initial stock)"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT 
                i.descripcion_insumo as producto,
                COALESCE(ei.cantidad, 0) AS cant_inicial,
                (COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) AS cant_final,
                ((COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) - COALESCE(ei.cantidad, 0)) AS variacion_unidades,
                (((COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) * i.costo_unitario) - (COALESCE(ei.cantidad, 0) * COALESCE(ei.costo, 0))) AS variacion_monto
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            ORDER BY ABS(variacion_unidades) DESC
            LIMIT 10
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def search_product_by_id(product_id: int) -> List[Dict]:
        """Search specific product by ID"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            f"""
            SELECT 
                i.id,
                i.descripcion_insumo as producto,
                i.costo_unitario,
                COALESCE(ei.cantidad, 0) AS cant_inicial,
                COALESCE(ei.costo, 0) AS costo_inicial,
                (COALESCE(ei.cantidad, 0) * COALESCE(ei.costo, 0)) AS monto_inicial,
                COALESCE(e.cantidad, 0) AS cant_entrada,
                COALESCE(e.costo, 0) AS costo_entrada,
                (COALESCE(e.cantidad, 0) * COALESCE(e.costo, 0)) AS monto_entrada,
                COALESCE(s.cantidad, 0) AS cant_salida,
                COALESCE(s.costo, 0) AS costo_salida,
                (COALESCE(s.cantidad, 0) * COALESCE(s.costo, 0)) AS monto_salida,
                (COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) AS cant_final,
                ((COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) * i.costo_unitario) AS monto_final
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            WHERE i.id = {product_id}
            LIMIT 1
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def search_product_by_description(description: str) -> List[Dict]:
        """Search products by description (partial match)"""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        
        description = description.replace("'", "''")
        
        cursor.execute(
            f"""
            SELECT 
                i.id,
                i.descripcion_insumo as producto,
                i.costo_unitario,
                COALESCE(ei.cantidad, 0) AS cant_inicial,
                COALESCE(ei.costo, 0) AS costo_inicial,
                (COALESCE(ei.cantidad, 0) * COALESCE(ei.costo, 0)) AS monto_inicial,
                COALESCE(e.cantidad, 0) AS cant_entrada,
                COALESCE(e.costo, 0) AS costo_entrada,
                (COALESCE(e.cantidad, 0) * COALESCE(e.costo, 0)) AS monto_entrada,
                COALESCE(s.cantidad, 0) AS cant_salida,
                COALESCE(s.costo, 0) AS costo_salida,
                (COALESCE(s.cantidad, 0) * COALESCE(s.costo, 0)) AS monto_salida,
                (COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) AS cant_final,
                ((COALESCE(ei.cantidad, 0) + COALESCE(e.cantidad, 0) - COALESCE(s.cantidad, 0)) * i.costo_unitario) AS monto_final
            FROM Inventario i
            LEFT JOIN existencia_inicial ei ON ei.inventario_id = i.id
            LEFT JOIN entradas e ON e.inventario_id = i.id
            LEFT JOIN salidas s ON s.inventario_id = i.id
            WHERE i.descripcion_insumo LIKE '%{description}%'
            LIMIT 5
            """
        )
        
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return datos
    
    @staticmethod
    def get_query_data(query_type: str, **kwargs) -> List[Dict]:
        """Factory method to get data for specific query types"""
        query_map = {
            "stock_bajo": lambda: InventoryQueries.get_low_stock_products(kwargs.get("threshold", 5)),
            "sin_stock": InventoryQueries.get_out_of_stock_products,
            "valor_inventario": InventoryQueries.get_inventory_value,
            "mas_entradas": InventoryQueries.get_top_entries,
            "mas_salidas": InventoryQueries.get_top_sales,
            "monto_entradas": InventoryQueries.get_total_entries,
            "monto_salidas": InventoryQueries.get_total_sales,
            "sin_movimiento": InventoryQueries.get_no_movement_products,
            "variacion_stock": InventoryQueries.get_stock_variation,
        }
        
        if query_type not in query_map:
            raise ValueError(f"Unknown query type: {query_type}")
        
        return query_map[query_type]()
    
    @staticmethod
    def search_product(search_term: str) -> List[Dict]:
        """Smart product search - tries ID first, then description"""
        search_term = search_term.strip()
        
        try:
            product_id = int(search_term)
            return InventoryQueries.search_product_by_id(product_id)
        except ValueError:
            return InventoryQueries.search_product_by_description(search_term)
