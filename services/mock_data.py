"""
Mock data for inventory system - simulates database responses
This will be replaced with real database queries later
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import random

def get_mock_inventory_data(query_type: str) -> List[Dict[str, Any]]:
    """
    Get mock data based on query type
    Returns simulated database results for testing purposes
    """
    
    if query_type == "low_stock":
        return [
            {"id": 1, "descripcion": "Acetaminofén 500mg", "stock_actual": 15, "stock_minimo": 50, "proveedor": "FarmaPlus"},
            {"id": 2, "descripcion": "Ibuprofeno 400mg", "stock_actual": 8, "stock_minimo": 30, "proveedor": "MediCorp"},
            {"id": 3, "descripcion": "Alcohol antiséptico", "stock_actual": 5, "stock_minimo": 25, "proveedor": "SanitarySA"},
            {"id": 4, "descripcion": "Guantes desechables", "stock_actual": 12, "stock_minimo": 100, "proveedor": "EquiMed"}
        ]
    
    elif query_type == "expiring_soon":
        today = datetime.now()
        return [
            {"id": 5, "descripcion": "Amoxicilina 500mg", "lote": "LOT2024A", "fecha_vencimiento": (today + timedelta(days=15)).strftime("%Y-%m-%d"), "stock": 45},
            {"id": 6, "descripcion": "Vitamina C masticable", "lote": "VIT2024B", "fecha_vencimiento": (today + timedelta(days=25)).strftime("%Y-%m-%d"), "stock": 80},
            {"id": 7, "descripcion": "Jarabe para la tos", "lote": "JAR2024C", "fecha_vencimiento": (today + timedelta(days=35)).strftime("%Y-%m-%d"), "stock": 20}
        ]
    
    elif query_type == "expired_products":
        today = datetime.now()
        return [
            {"id": 8, "descripcion": "Aspirina 100mg", "lote": "ASP2023X", "fecha_vencimiento": (today - timedelta(days=30)).strftime("%Y-%m-%d"), "stock": 25},
            {"id": 9, "descripcion": "Crema antibiótica", "lote": "CRE2023Y", "fecha_vencimiento": (today - timedelta(days=15)).strftime("%Y-%m-%d"), "stock": 10}
        ]
    
    elif query_type == "top_selling":
        return [
            {"id": 10, "descripcion": "Acetaminofén 500mg", "ventas_mes": 450, "ingresos": 22500, "rotacion": "Alta"},
            {"id": 11, "descripcion": "Ibuprofeno 400mg", "ventas_mes": 380, "ingresos": 19000, "rotacion": "Alta"},
            {"id": 12, "descripcion": "Vitaminas multiples", "ventas_mes": 320, "ingresos": 24000, "rotacion": "Media-Alta"},
            {"id": 13, "descripcion": "Termómetro digital", "ventas_mes": 85, "ingresos": 17000, "rotacion": "Media"}
        ]
    
    elif query_type == "low_rotation":
        return [
            {"id": 14, "descripcion": "Vendas elásticas", "ultima_venta": "2024-01-15", "stock": 150, "meses_sin_movimiento": 4},
            {"id": 15, "descripcion": "Suero fisiológico 1L", "ultima_venta": "2024-02-20", "stock": 200, "meses_sin_movimiento": 3},
            {"id": 16, "descripcion": "Tensiómetro manual", "ultima_venta": "2023-12-10", "stock": 25, "meses_sin_movimiento": 5}
        ]
    
    elif query_type == "inventory_value":
        return [
            {"categoria": "Medicamentos", "total_costo": 85000, "total_venta": 127500, "margen": 50},
            {"categoria": "Equipos médicos", "total_costo": 45000, "total_venta": 72000, "margen": 60},
            {"categoria": "Insumos", "total_costo": 20000, "total_venta": 28000, "margen": 40},
            {"total_general": {"costo_total": 150000, "precio_venta_total": 227500, "margen_promedio": 51.6}}
        ]
    
    elif query_type == "price_changes":
        return [
            {"id": 17, "descripcion": "Mascarillas N95", "precio_anterior": 2500, "precio_actual": 3000, "cambio_fecha": "2024-03-01", "motivo": "Inflación proveedor"},
            {"id": 18, "descripcion": "Alcohol gel 500ml", "precio_anterior": 8000, "precio_actual": 7500, "cambio_fecha": "2024-03-15", "motivo": "Promoción"},
            {"id": 19, "descripcion": "Glucómetro", "precio_anterior": 65000, "precio_actual": 72000, "cambio_fecha": "2024-02-28", "motivo": "Actualización modelo"}
        ]
    
    elif query_type == "supplier_alerts":
        return [
            {"proveedor": "FarmaPlus", "productos_agotandose": 8, "productos_venciendo": 3, "alertas_totales": 11},
            {"proveedor": "MediCorp", "productos_agotandose": 5, "productos_venciendo": 2, "alertas_totales": 7},
            {"proveedor": "SanitarySA", "productos_agotandose": 12, "productos_venciendo": 1, "alertas_totales": 13}
        ]
    
    elif query_type == "product_history":
        return [
            {"fecha": "2024-03-15", "tipo": "Entrada", "cantidad": 100, "motivo": "Compra", "lote": "LOT2024X"},
            {"fecha": "2024-03-10", "tipo": "Salida", "cantidad": 25, "motivo": "Venta", "cliente": "Cliente A"},
            {"fecha": "2024-03-08", "tipo": "Salida", "cantidad": 15, "motivo": "Venta", "cliente": "Cliente B"},
            {"fecha": "2024-03-01", "tipo": "Entrada", "cantidad": 50, "motivo": "Restock", "lote": "LOT2024Y"}
        ]
    
    elif query_type == "loss_analysis":
        return [
            {"producto": "Jarabe pediátrico", "perdidas_vencimiento": 35, "valor_perdido": 87500, "motivo": "Baja rotación"},
            {"producto": "Suplementos vitamínicos", "perdidas_vencimiento": 20, "valor_perdido": 45000, "motivo": "Sobrestockeado"},
            {"producto": "Medicamento especializado", "perdidas_devolucion": 8, "valor_perdido": 120000, "motivo": "Defecto fabricante"}
        ]
    
    elif query_type == "excess_stock":
        return [
            {"id": 20, "descripcion": "Vendas medianas", "stock_actual": 500, "stock_minimo": 50, "exceso": 450, "costo_exceso": 22500},
            {"id": 21, "descripcion": "Algodón hidrofilo", "stock_actual": 300, "stock_minimo": 75, "exceso": 225, "costo_exceso": 11250},
            {"id": 22, "descripcion": "Jeringas 5ml", "stock_actual": 800, "stock_minimo": 100, "exceso": 700, "costo_exceso": 35000}
        ]
    
    elif query_type == "out_of_stock":
        return [
            {"id": 23, "descripcion": "Mascarillas quirúrgicas", "stock_actual": 0, "ultima_venta": "2024-03-20", "demanda_promedio": 150},
            {"id": 24, "descripcion": "Guantes estériles L", "stock_actual": 0, "ultima_venta": "2024-03-19", "demanda_promedio": 80},
            {"id": 25, "descripcion": "Termómetros digitales", "stock_actual": 0, "ultima_venta": "2024-03-18", "demanda_promedio": 25}
        ]
    
    elif query_type == "urgent_restock":
        return [
            {"id": 26, "descripcion": "Paracetamol pediatrico", "stock_actual": 5, "stock_minimo": 30, "ventas_ultimos_7_dias": 15, "dias_hasta_agotarse": 2},
            {"id": 27, "descripcion": "Suero oral", "stock_actual": 8, "stock_minimo": 40, "ventas_ultimos_7_dias": 12, "dias_hasta_agotarse": 4},
            {"id": 28, "descripcion": "Antiacido liquido", "stock_actual": 3, "stock_minimo": 25, "ventas_ultimos_7_dias": 8, "dias_hasta_agotarse": 3}
        ]
    
    else:
        # Default fallback data
        return [
            {"mensaje": "Datos de prueba", "query_type": query_type, "timestamp": datetime.now().isoformat()}
        ]

def get_formatted_response_data(query_type: str) -> str:
    """
    Get a formatted text summary of the mock data
    Used when AI service is not available
    """
    data = get_mock_inventory_data(query_type)
    
    if query_type == "low_stock":
        return f"📉 Productos con stock bajo:\n\n" + "\n".join([
            f"• {item['descripcion']}: {item['stock_actual']} unidades (mín: {item['stock_minimo']})"
            for item in data
        ])
    
    elif query_type == "expiring_soon":
        return f"⏰ Productos próximos a vencer:\n\n" + "\n".join([
            f"• {item['descripcion']} (Lote: {item['lote']}): vence {item['fecha_vencimiento']}"
            for item in data
        ])
    
    elif query_type == "expired_products":
        return f"❌ Productos vencidos:\n\n" + "\n".join([
            f"• {item['descripcion']} (Lote: {item['lote']}): venció {item['fecha_vencimiento']}"
            for item in data
        ])
    
    elif query_type == "inventory_value":
        total = data[-1]["total_general"]
        return f"💰 Valor total del inventario:\n\n• Costo: ${total['costo_total']:,}\n• Precio venta: ${total['precio_venta_total']:,}\n• Margen: {total['margen_promedio']:.1f}%"
    
    else:
        return f"📊 Datos encontrados: {len(data)} registros para consulta '{query_type}'"
