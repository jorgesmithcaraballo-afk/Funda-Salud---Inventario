"""
Domain Models Package
Contains all data structures, enums, and DTOs for the inventory system
"""

from .inventory_models import (
    QueryType,
    InventoryQuery,
    QueryResult,
    AIServiceConfig
)

__all__ = [
    "QueryType",
    "InventoryQuery", 
    "QueryResult",
    "AIServiceConfig"
]
