"""
Services Package
Contains all business logic services for the inventory system
"""

from .ai_service import InventoryAIService, get_ai_service

__all__ = [
    "InventoryAIService",
    "get_ai_service"
]
