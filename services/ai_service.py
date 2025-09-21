"""
AI Service for intelligent inventory queries and analysis
Centralizes all AI logic in a reusable, clean architecture module
Updated with 10 comprehensive inventory queries and mock data support
"""

import google.generativeai as genai
from conexion import obtener_conexion
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from models.inventory_models import InventoryQuery, QueryResult, AIServiceConfig, QueryType
from services.mock_data import get_mock_inventory_data, get_formatted_response_data


class ResponseFormatter:
    """Unified response formatter for consistent chat-style outputs"""
    
    @staticmethod
    def format(data: List[Dict], user_prompt: str, query_type: str = "general") -> str:
        """
        Format response in consistent 3-step format:
        1. Summary line
        2. Max 5 items with bullets
        3. Recommendation line
        """
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not data:
            return f"❌ No se encontraron resultados para tu consulta.\n\n💡 **Recomendación:** Verifica los filtros o intenta con una consulta diferente."
        
        # 1. Summary line
        summary = f"📊 **Encontrados:** {len(data)} registro(s) | 📅 {current_datetime}"
        
        # 2. Item list (max 5 with smart field selection)
        items_text = ResponseFormatter._format_item_list(data, query_type)
        
        # 3. Smart recommendation based on query type
        recommendation = ResponseFormatter._get_smart_recommendation(query_type, len(data))
        
        return f"{summary}\n\n{items_text}\n\n{recommendation}"
    
    @staticmethod
    def format_ai_response(ai_text: str, data: List[Dict], query_type: str = "general") -> str:
        """
        Format AI response ensuring it follows the 3-step format
        If AI response is too long or doesn't follow format, apply formatting
        """
        if not ai_text or len(ai_text.split('\n')) > 15:
            # AI response too long or missing, use formatted fallback
            return ResponseFormatter.format(data, "Análisis de inventario", query_type)
        
        # Check if AI response already has good format
        lines = ai_text.split('\n')
        if len(lines) <= 10 and any('•' in line or '1.' in line for line in lines):
            # AI response looks well formatted, return as is
            return ai_text
        
        # AI response exists but needs better formatting
        return ai_text[:500] + "..." if len(ai_text) > 500 else ai_text
    
    @staticmethod
    def _format_item_list(data: List[Dict], query_type: str) -> str:
        """Format list of items with smart field selection based on query type"""
        if not data:
            return "• No hay datos disponibles"
        
        # Show max 5 items
        items_to_show = data[:5]
        items = []
        
        for i, item in enumerate(items_to_show, 1):
            # Smart field selection based on query type
            if query_type in ["low_stock", "urgent_restock", "out_of_stock"]:
                desc = item.get('descripcion', item.get('producto', 'Producto'))
                stock = item.get('stock_actual', item.get('stock', 'N/A'))
                items.append(f"• **{desc}** - Stock: {stock}")
                
            elif query_type in ["expiring_soon", "expired_products"]:
                desc = item.get('descripcion', item.get('producto', 'Producto'))
                fecha = item.get('fecha_vencimiento', item.get('fecha', 'N/A'))
                items.append(f"• **{desc}** - Vence: {fecha}")
                
            elif query_type == "inventory_value":
                costo = item.get('valor_costo', item.get('costo_total', 'N/A'))
                venta = item.get('valor_venta', item.get('venta_total', 'N/A'))
                items.append(f"• **Costo total:** ${costo:,} | **Venta:** ${venta:,}")
                
            elif query_type in ["top_selling", "low_rotation"]:
                desc = item.get('descripcion', item.get('producto', 'Producto'))
                ventas = item.get('ventas_totales', item.get('ventas_mes', 'N/A'))
                items.append(f"• **{desc}** - Ventas: {ventas}")
                
            else:
                # Generic format
                desc = item.get('descripcion', item.get('producto', f'Item {i}'))
                items.append(f"• **{desc}**")
        
        # Add "more items" indicator if needed
        if len(data) > 5:
            items.append(f"• ... y {len(data) - 5} productos más")
        
        return '\n'.join(items)
    
    @staticmethod
    def _get_smart_recommendation(query_type: str, item_count: int) -> str:
        """Generate smart recommendation based on query type"""
        recommendations = {
            "low_stock": "🚨 **Acción Urgente:** Reabastecer productos con stock bajo para evitar desabastecimiento. Contactar proveedores y programar pedidos inmediatos. Revisar frecuencias de pedido.",
            "urgent_restock": "⚡ **Crítico:** Contactar proveedores inmediatamente para restock crítico. Priorizar estos productos en próximos pedidos para evitar pérdida de ventas.",
            "expiring_soon": "⏰ **Acción Inmediata:** Aplicar descuentos o promociones antes del vencimiento. Implementar estrategia FEFO (First Expired, First Out) para rotación.",
            "expired_products": "❌ **Crítico:** Retirar productos vencidos del inventario inmediatamente. Documentar pérdidas y revisar procesos de rotación de stock.",
            "out_of_stock": "🚫 **Urgente:** Restablecer stock de productos agotados para evitar pérdida de ventas. Evaluar demanda histórica para ajustar niveles mínimos.",
            "top_selling": "🏆 **Oportunidad:** Aumentar stock de productos top para maximizar ventas. Negociar mejores precios por volumen con proveedores.",
            "low_rotation": "🐌 **Estrategia:** Revisar precios y marketing de productos de baja rotación. Considerar liquidación o cambios en la estrategia comercial.",
            "inventory_value": "💰 **Análisis:** Monitorear el valor total para optimizar capital de trabajo. Balancear niveles de inventario con flujo de caja.",
            "price_changes": "📈 **Seguimiento:** Evaluar impacto de cambios de precio en las ventas. Monitorear competencia y ajustar estrategia de precios.",
            "excess_stock": "📦 **Optimización:** Reducir exceso de stock para liberar capital. Implementar promociones o renegociar con proveedores."
        }
        
        return recommendations.get(query_type, "💡 **Recomendación:** Revisar datos regularmente para optimizar inventario y mejorar la gestión de stock.")


class InventoryAIService:
    """AI service specialized in intelligent inventory queries and analysis"""
    
    def __init__(self, config: AIServiceConfig):
        """
        Initialize AI service with configuration
        
        Args:
            config: AI service configuration object
        """
        self._config = config
        self._model = None
        self._use_mock_data = True  # Toggle between mock and real database
        
        if config.api_key and config.api_key != "TU_API_KEY_AQUI":
            self._initialize_ai_model(config.api_key)
            self._config.is_configured = True
        
        # Specialized context for inventory management
        self._system_prompt = """
        You are a specialized assistant for inventory management and data analysis.
        
        INVENTORY SYSTEM CONTEXT:
        - You work with pharmaceutical/medical supplies inventory
        - Focus on stock levels, expiration dates, supplier management, sales patterns
        - Provide practical recommendations for inventory optimization
        
        FECHA Y HORA ACTUAL DEL SISTEMA: {current_datetime}
        - Usa esta fecha para calcular si productos están vencidos o próximos a vencer
        - Calcula días hasta vencimiento basándote en esta fecha actual
        - Determina urgencia de reabastecimiento según esta fecha
        
        FORMATO DE RESPUESTA OBLIGATORIO:
        
        1. Resumen inicial:
        Comienza con un resumen del número total de resultados encontrados
        2. Listado:
        Máximo 5 productos en formato de lista con 2-3 datos clave por producto:
           - Usa viñetas (•) o números  
           - Incluye datos como: stock actual, stock mínimo, fecha vencimiento, precio, etc.
           - Mantén cada línea de producto corta y clara
        3. Recomendación:
        Agrega una recomendación breve, general y práctica al final
        
        REGLAS DE FORMATO:
        - NO uses tablas grandes
        - Usa listas cortas estilo mensajes de chat
        - Responde siempre en español
        - Usa emojis para hacer las respuestas más atractivas
        - Sé conciso pero informativo (max 250 palabras)
        - Incluye números específicos y fechas cuando estén disponibles
        - Sugiere pasos de acción concretos
        - Enfócate en el impacto del negocio y eficiencia operacional
        """
    
    def _initialize_ai_model(self, api_key: str) -> None:
        """Initialize Google Gemini AI model"""
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel('gemini-1.5-flash-8b')
        except Exception as e:
            print(f"Error initializing AI model: {e}")
            self._config.is_configured = False
    
    def get_predefined_queries(self) -> Dict[str, InventoryQuery]:
        """
        Get predefined system queries - 10 inventory questions
        
        Returns:
            Dictionary with the 10 main system queries
        """
        
        queries = {
            QueryType.LOW_STOCK: InventoryQuery(
                query_type=QueryType.LOW_STOCK,
                title="¿Qué productos necesitan restock urgente?",
                icon="", 
                color="#dc3545",
                description="Productos próximos a agotarse",
                sql_query="SELECT * FROM Inventario WHERE stock_actual <= stock_minimo ORDER BY (stock_actual/stock_minimo) ASC",
                user_prompt="¿Qué productos están próximos a agotarse y necesitan reabastecimiento urgente?"
            ),
            
            QueryType.EXPIRING_SOON: InventoryQuery(
                query_type=QueryType.EXPIRING_SOON,
                title="¿Qué productos vencen en los próximos 30 días?",
                icon="",
                color="#f39c12",
                description="Productos con vencimiento cercano (próximos 30 días)",
                sql_query="SELECT * FROM Inventario WHERE fecha_vencimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) ORDER BY fecha_vencimiento ASC",
                user_prompt="¿Qué productos tienen fecha de vencimiento cercana?"
            ),
            
            QueryType.EXPIRED_PRODUCTS: InventoryQuery(
                query_type=QueryType.EXPIRED_PRODUCTS,
                title="¿Qué productos ya están vencidos?",
                icon="",
                color="#c0392b",
                description="Productos ya vencidos",
                sql_query="SELECT * FROM Inventario WHERE fecha_vencimiento < CURDATE() ORDER BY fecha_vencimiento ASC",
                user_prompt="¿Qué productos ya están vencidos?"
            ),
            
            QueryType.TOP_SELLING: InventoryQuery(
                query_type=QueryType.TOP_SELLING,
                title="¿Cuáles son los productos más vendidos?",
                icon="",
                color="#27ae60",
                description="Productos más vendidos (último mes/trimestre)",
                sql_query="SELECT p.*, SUM(s.cantidad) as ventas_totales FROM Inventario p JOIN salidas s ON p.id = s.inventario_id WHERE s.fecha >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) GROUP BY p.id ORDER BY ventas_totales DESC LIMIT 10",
                user_prompt="¿Cuáles son los productos más vendidos en el último período?"
            ),
            
            QueryType.LOW_ROTATION: InventoryQuery(
                query_type=QueryType.LOW_ROTATION,
                title="¿Qué productos tienen baja rotación de ventas?",
                icon="", 
                color="#95a5a6",
                description="Productos con baja rotación",
                sql_query="SELECT * FROM Inventario WHERE id NOT IN (SELECT DISTINCT inventario_id FROM salidas WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)) ORDER BY cantidad DESC",
                user_prompt="¿Cuáles son los productos con baja rotación?"
            ),
            
            QueryType.INVENTORY_VALUE: InventoryQuery(
                query_type=QueryType.INVENTORY_VALUE,
                title="¿Cuál es el valor total del inventario?",
                icon="",
                color="#3498db", 
                description="Valor total (costo y venta)",
                sql_query="SELECT SUM(cantidad * costo_unitario) as valor_costo, SUM(cantidad * precio_venta) as valor_venta FROM Inventario",
                user_prompt="¿Cuál es el valor total actual del inventario?"
            ),
            
            QueryType.PRICE_CHANGES: InventoryQuery(
                query_type=QueryType.PRICE_CHANGES,
                title="¿Qué productos cambiaron de precio recientemente?",
                icon="",
                color="#9b59b6",
                description="Cambios de precio recientes",
                sql_query="SELECT * FROM Inventario WHERE fecha_ultimo_cambio_precio >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) ORDER BY fecha_ultimo_cambio_precio DESC",
                user_prompt="¿Qué productos han cambiado de precio recientemente?"
            ),
            
            QueryType.EXCESS_STOCK: InventoryQuery(
                query_type=QueryType.EXCESS_STOCK,
                title="¿Qué productos tienen exceso de inventario?",
                icon="",
                color="#e67e22",
                description="Productos con exceso de stock",
                sql_query="SELECT *, (stock_actual - stock_minimo) as exceso FROM Inventario WHERE stock_actual > stock_minimo * 3 ORDER BY exceso DESC",
                user_prompt="¿Qué productos tienen exceso de stock?"
            ),
            
            QueryType.OUT_OF_STOCK: InventoryQuery(
                query_type=QueryType.OUT_OF_STOCK,
                title="¿Qué productos están completamente agotados?",
                icon="",
                color="#721c24",
                description="Productos agotados",
                sql_query="SELECT * FROM Inventario WHERE stock_actual = 0",
                user_prompt="¿Qué productos están agotados?"
            ),
            
            QueryType.URGENT_RESTOCK: InventoryQuery(
                query_type=QueryType.URGENT_RESTOCK,
                title="¿Qué productos requieren pedido inmediato?",
                icon="", 
                color="#d63384",
                description="Productos que requieren reabastecimiento inmediato",
                sql_query="SELECT * FROM Inventario WHERE stock_actual <= stock_minimo AND stock_actual > 0 ORDER BY stock_actual ASC",
                user_prompt="¿Qué productos requieren reabastecimiento inmediato?"
            )
        }
        
        
        return {q.query_type.value: q for q in queries.values()}
    
    def execute_sql_query(self, sql_query: str) -> List[Dict]:
        """
        Execute SQL query and return results
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            List of dictionaries with query results
        """
        if self._use_mock_data:
            # For now, return mock data instead of executing real queries
            # This will be updated to real database queries later
            return []  # Mock data is handled separately
        
        try:
            conn = obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            print(f"Error executing SQL: {e}")
            return []
    
    def generate_ai_response(self, user_prompt: str, data: List[Dict], query_type: str = "general") -> str:
        """
        Generate intelligent response using Gemini AI with ResponseFormatter
        
        Args:
            user_prompt: User's question/prompt
            data: Data obtained from database or mock
            query_type: Type of query for smart formatting
            
        Returns:
            AI-generated response
        """
        if not self._config.is_configured:
            return ResponseFormatter.format(data, user_prompt, query_type)
        
        # Get current date and time for accurate calculations
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format system prompt with current date
        formatted_system_prompt = self._system_prompt.format(current_datetime=current_datetime)
        
        prompt = f"""
        {formatted_system_prompt}
        
        USER QUERY: "{user_prompt}"
        QUERY TYPE: "{query_type}"
        
        INVENTORY DATA TO ANALYZE:
        {json.dumps(data, indent=2, default=str)}
        
        NUMBER OF RECORDS: {len(data)}
        
        Based on this inventory data, provide:
        1. Key insights and analysis of the current situation
        2. Identification of critical issues or opportunities
        3. Specific and actionable recommendations
        4. Business impact assessment when relevant
        5. Use the current system date/time above for all expiration and date calculations
        
        Focus on practical value for inventory management decisions.
        IMPORTANT: Keep response concise (max 10 lines) and follow the chat format.
        """
        
        try:
            response = self._model.generate_content(prompt)
            # Use ResponseFormatter to ensure consistent format
            return ResponseFormatter.format_ai_response(response.text, data, query_type)
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return ResponseFormatter.format(data, user_prompt, query_type)
    
    def _generate_fallback_response(self, data: List[Dict], user_prompt: str, query_type: str = "general") -> str:
        """
        Generate simple response without AI using ResponseFormatter
        
        Args:
            data: Query data
            user_prompt: Original question
            query_type: Type of query for smart formatting
            
        Returns:
            Formatted response without AI
        """
        # Use ResponseFormatter for consistent output even without AI
        return ResponseFormatter.format(data, user_prompt, query_type)
    
    def process_query(self, query_key: str) -> QueryResult:
        """
        Process complete query (Data + AI Analysis)
        
        Args:
            query_key: Selected query key
            
        Returns:
            QueryResult object with response and data
        """
        start_time = time.time()
        
        try:
            queries = self.get_predefined_queries()
            
            if query_key not in queries:
                return QueryResult(
                    success=False,
                    data=[],
                    error_message="❌ Consulta no encontrada"
                )
            
            query = queries[query_key]
            
            # 1. Get data (mock for now, will be SQL later)
            if self._use_mock_data:
                sql_data = get_mock_inventory_data(query_key)
            else:
                sql_data = self.execute_sql_query(query.sql_query)
            
            # 2. Generate AI response with query type for smart formatting
            ai_response = self.generate_ai_response(query.user_prompt, sql_data, query_key)
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                success=True,
                data=sql_data,
                ai_response=ai_response,
                execution_time=execution_time
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                error_message=f"❌ Error procesando consulta: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current AI service status
        
        Returns:
            Dictionary with service status information
        """
        return {
            "is_configured": self._config.is_configured,
            "api_key_present": self._config.api_key is not None,
            "model": self._config.model_name if self._config.is_configured else None,
            "available_queries": len(self.get_predefined_queries()),
            "using_mock_data": self._use_mock_data
        }


# Global service instance (Singleton pattern)
_ai_service_instance = None

def get_ai_service(api_key: Optional[str] = None) -> InventoryAIService:
    """
    Factory function to get AI service instance
    
    Args:
        api_key: Gemini API key (only needed first time)
        
    Returns:
        AI service instance
    """
    global _ai_service_instance
    
    if _ai_service_instance is None:
        config = AIServiceConfig(api_key=api_key)
        _ai_service_instance = InventoryAIService(config)
    
    return _ai_service_instance