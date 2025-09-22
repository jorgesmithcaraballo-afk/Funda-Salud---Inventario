"""
Inventory domain models and data structures
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class QueryType(Enum):
    """Enumeration of predefined inventory query types based on real data structure"""
    STOCK_BAJO = "stock_bajo"  # Stock Bajo - Existencia Final ≤ umbral
    SIN_STOCK = "sin_stock"    # Sin Stock - Existencia Final = 0
    VALOR_INVENTARIO = "valor_inventario"  # Valor Total del Inventario - SUMA(O)
    MAS_ENTRADAS = "mas_entradas"  # Más Entradas - ordenar por Monto Total Entradas (I)
    MAS_SALIDAS = "mas_salidas"   # Más Salidas - ordenar por Monto Total Salidas (L)
    MONTO_ENTRADAS = "monto_entradas"  # Monto Total Entradas - SUMA(I)
    MONTO_SALIDAS = "monto_salidas"    # Monto Total Salidas - SUMA(L)
    SIN_MOVIMIENTO = "sin_movimiento"  # Sin Movimiento - Entradas (G) = 0 y Salidas (J) = 0
    VARIACION_STOCK = "variacion_stock"  # Variación de Stock - Final (M) – Inicial (E)
    PRODUCTO_LIBRE = "producto_libre"    # Pregunta Libre - buscar por ID o descripción


@dataclass
class InventoryQuery:
    """Data structure for inventory query configuration"""
    query_type: QueryType
    title: str
    icon: str
    color: str
    description: str
    sql_query: str
    user_prompt: str
    
    
@dataclass  
class QueryResult:
    """Data structure for query execution results"""
    success: bool
    data: List[Dict[str, Any]]
    ai_response: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    

@dataclass
class AIServiceConfig:
    """Configuration for AI service"""
    api_key: Optional[str] = None
    model_name: str = "gemini-1.5-flash-8b"
    max_response_length: int = 250
    is_configured: bool = False
