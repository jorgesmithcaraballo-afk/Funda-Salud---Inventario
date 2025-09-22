"""
Inventory domain models and data structures
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class QueryType(Enum):
    """Enumeration of predefined inventory query types"""
    LOW_STOCK = "low_stock"
    EXPIRING_SOON = "expiring_soon" 
    EXPIRED_PRODUCTS = "expired_products"
    TOP_SELLING = "top_selling"
    LOW_ROTATION = "low_rotation"
    INVENTORY_VALUE = "inventory_value"
    PRICE_CHANGES = "price_changes"
    EXCESS_STOCK = "excess_stock"
    OUT_OF_STOCK = "out_of_stock"
    URGENT_RESTOCK = "urgent_restock"


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
