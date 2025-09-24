"""
Servicio de aplicación para la vista de Chat AI.

Envuelve `controllers/chat_controller.py` para ofrecer una API estable orientada a la UI.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from controllers.chat_controller import ChatController
from models.inventory_models import QueryResult


class ChatAIAppService:
    """Fachada de aplicación para Chat AI, delega en ChatController."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._controller = ChatController(api_key)

    def set_query_callbacks(
        self,
        on_started: Optional[Callable] = None,
        on_completed: Optional[Callable[[QueryResult], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._controller.set_query_callbacks(on_started, on_completed, on_error)

    def get_available_queries(self) -> Dict[str, Any]:
        return self._controller.get_available_queries()

    def execute_query_async(self, query_key: str) -> None:
        self._controller.execute_query_async(query_key)

    def search_product_async(self, search_term: str) -> None:
        self._controller.search_product_async(search_term)

    def is_ai_configured(self) -> bool:
        return self._controller.is_ai_configured()

