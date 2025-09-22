"""
Chat Controller - Handles business logic for AI chat functionality
Separates UI concerns from business logic following Clean Architecture principles
"""
from typing import Dict, Any, Callable, Optional
from services.ai_service import get_ai_service
from models.inventory_models import QueryResult, QueryType
import threading


class ChatController:
    """Controller for handling AI chat business logic"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize chat controller
        
        Args:
            api_key: Optional API key for AI service
        """
        self._ai_service = get_ai_service(api_key)
        self._on_query_started: Optional[Callable] = None
        self._on_query_completed: Optional[Callable[[QueryResult], None]] = None
        self._on_query_error: Optional[Callable[[str], None]] = None
    
    def set_query_callbacks(self, 
                           on_started: Callable = None,
                           on_completed: Callable[[QueryResult], None] = None,
                           on_error: Callable[[str], None] = None) -> None:
        """
        Set callbacks for query events
        
        Args:
            on_started: Called when query execution starts
            on_completed: Called when query completes successfully
            on_error: Called when query fails
        """
        self._on_query_started = on_started
        self._on_query_completed = on_completed
        self._on_query_error = on_error
    
    def get_available_queries(self) -> Dict[str, Any]:
        """
        Get available queries for UI rendering
        
        Returns:
            Dictionary with query configurations
        """
        queries = self._ai_service.get_predefined_queries()
        
        # Convert to UI-friendly format
        ui_queries = {}
        for key, query in queries.items():
            ui_queries[key] = {
                "title": query.title,
                "icon": query.icon,
                "color": query.color,
                "description": query.description
            }
        
        return ui_queries
    
    
    def execute_query_async(self, query_key: str) -> None:
        """
        Execute query asynchronously to avoid blocking UI
        
        Args:
            query_key: Key of the query to execute
        """
        if self._on_query_started:
            self._on_query_started()
        
        # Execute in background thread
        thread = threading.Thread(
            target=self._process_query_background,
            args=(query_key,),
            daemon=True
        )
        thread.start()
    
    def search_product_async(self, search_term: str) -> None:
        """
        Search for a specific product by ID or description
        
        Args:
            search_term: ID or description to search for
        """
        if self._on_query_started:
            self._on_query_started()
        
        # Execute in background thread
        thread = threading.Thread(
            target=self._process_product_search_background,
            args=(search_term,),
            daemon=True
        )
        thread.start()
    
    def _process_product_search_background(self, search_term: str) -> None:
        """
        Process product search in background thread
        
        Args:
            search_term: Product search term
        """
        try:
            result = self._ai_service.search_specific_product(search_term)
            
            if result.success and self._on_query_completed:
                self._on_query_completed(result)
            elif not result.success and self._on_query_error:
                self._on_query_error(result.error_message or "No se encontró el producto")
                
        except Exception as e:
            if self._on_query_error:
                self._on_query_error(f"Error en búsqueda: {str(e)}")
    
    def _process_query_background(self, query_key: str) -> None:
        """
        Process query in background thread
        
        Args:
            query_key: Query key to process
        """
        try:
            result = self._ai_service.process_query(query_key)
            
            if result.success and self._on_query_completed:
                self._on_query_completed(result)
            elif not result.success and self._on_query_error:
                self._on_query_error(result.error_message or "Unknown error occurred")
                
        except Exception as e:
            if self._on_query_error:
                self._on_query_error(f"Unexpected error: {str(e)}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get AI service configuration status
        
        Returns:
            Service status information
        """
        return self._ai_service.get_status()
    
    def is_ai_configured(self) -> bool:
        """
        Check if AI is properly configured
        
        Returns:
            True if AI is configured and ready
        """
        status = self.get_service_status()
        return status.get("is_configured", False)
