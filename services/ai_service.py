"""
AI Service for intelligent inventory queries and analysis
Centralizes all AI logic in a reusable, clean architecture module
Updated with 10 comprehensive inventory queries and mock data support
"""

import google.generativeai as genai
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from models.inventory_models import (
    InventoryQuery,
    QueryResult,
    AIServiceConfig,
    QueryType,
)
from services.domain.inventory_queries import InventoryQueries


class ResponseFormatter:
    """Unified response formatter for consistent chat-style outputs"""

    # Static header to prepend to LOCAL (fallback) responses only
    PREFIX = (
        "Respuesta del Sistema.\n"
        "IA no disponible, mostrando resultados:\n\n"
    )

    @staticmethod
    def _with_prefix(text: str) -> str:
        """Ensure the response starts with the standard header once."""
        try:
            if not text:
                return ResponseFormatter.PREFIX
            # Avoid duplicating if already present
            if text.startswith("Respuesta del Sistema."):
                return text
            return f"{ResponseFormatter.PREFIX}{text}"
        except Exception:
            return f"{ResponseFormatter.PREFIX}{text or ''}"

    @staticmethod
    def format(data: List[Dict], user_prompt: str, query_type: str = "general") -> str:
        """
        Format LOCAL response (fallback) in consistent 3-step format:
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
        recommendation = ResponseFormatter._get_smart_recommendation(
            query_type, len(data)
        )

        body = f"{summary}\n\n{items_text}\n\n{recommendation}"
        return ResponseFormatter._with_prefix(body)

    @staticmethod
    def format_ai_response(
        ai_text: str, data: List[Dict], query_type: str = "general"
    ) -> str:
        """
        AI response passthrough. The LLM formats the response via prompt.
        Only fallback to local formatting if missing/empty.
        """
        if not ai_text or not ai_text.strip():
            return ResponseFormatter.format(data, "Análisis de inventario", query_type)
        # If extremely long, trim but do not add local prefix
        return ai_text if len(ai_text) <= 600 else (ai_text[:600] + "...")

    @staticmethod
    def _format_item_list(data: List[Dict], query_type: str) -> str:
        """Format list of items with smart field selection based on query type"""

        def _to_float(value: Any, default: float = 0.0) -> float:
            """Safely convert value to float; fallback to default if None/invalid."""
            try:
                if value is None:
                    return default
                return float(value)
            except Exception:
                return default

        if not data:
            return "• No hay datos disponibles"

        # Show max 5 items
        items_to_show = data[:5]
        items = []

        for i, item in enumerate(items_to_show, 1):
            # Smart field selection based on query type - clean formatting
            if query_type in ["stock_bajo", "sin_stock"]:
                desc = item.get("descripcion", item.get("producto", "Producto"))
                stock = item.get("existencia_final", item.get("stock", "N/A"))
                precio = _to_float(item.get("costo_unitario", 0))
                items.append(f"• {desc}\n  Stock: {stock} | Precio: ${precio:.2f}")

            elif query_type == "valor_inventario":
                desc = item.get("tipo", item.get("producto", "Total"))
                valor = _to_float(item.get("valor_total", item.get("monto_final")))
                if desc == "TOTAL":
                    items.append(f"• VALOR TOTAL INVENTARIO: ${valor:.2f}")
                else:
                    items.append(f"• {desc}: ${valor:.2f}")

            elif query_type in ["mas_entradas", "mas_salidas"]:
                desc = item.get("producto", "Producto")
                cantidad = item.get("cant_entrada", item.get("cant_salida", "N/A"))
                monto = _to_float(item.get("monto_entrada", item.get("monto_salida")))
                items.append(f"• {desc}\n  Cantidad: {cantidad} | Monto: ${monto:.2f}")

            elif query_type in ["monto_entradas", "monto_salidas"]:
                tipo = item.get("tipo", "Item")
                monto = _to_float(
                    item.get("monto_total_entradas", item.get("monto_total_salidas"))
                )
                if "TOTAL" in tipo:
                    items.append(f"• {tipo}: ${monto:.2f}")
                else:
                    items.append(f"• {tipo}: ${monto:.2f}")

            elif query_type == "sin_movimiento":
                desc = item.get("producto", "Producto")
                inicial = item.get("cant_inicial", 0)
                final = item.get("existencia_final", 0)
                items.append(
                    f"• {desc}\n  Stock inicial: {inicial} | Stock final: {final}"
                )

            elif query_type == "variacion_stock":
                desc = item.get("producto", "Producto")
                inicial = item.get("cant_inicial", 0)
                final = item.get("cant_final", 0)
                variacion = item.get("variacion_unidades", 0)
                items.append(
                    f"• {desc}\n  Inicial: {inicial} | Final: {final} | Variación: {variacion:+}"
                )

            else:
                # Generic format
                desc = item.get("descripcion", item.get("producto", f"Item {i}"))
                items.append(f"• {desc}")

        # Add "more items" indicator if needed
        if len(data) > 5:
            items.append(f"• ... y {len(data) - 5} productos más")

        return "\n".join(items)

    @staticmethod
    def _get_smart_recommendation(query_type: str, item_count: int) -> str:
        """Generate smart recommendation based on query type for inventory management"""
        recommendations = {
            "stock_bajo": "🚨 Acción Urgente:\nReabastecer productos con stock bajo para evitar desabastecimiento.\n\nPasos inmediatos:\n• Contactar proveedores de estos productos\n• Programar pedidos de emergencia\n• Revisar puntos de reorden\n• Considerar proveedores alternativos",
            "sin_stock": "🚫 Crítico - Stock Agotado:\nRestablecer inventario de productos agotados inmediatamente.\n\nAcciones requeridas:\n• Contactar proveedores urgentemente\n• Evaluar demanda perdida\n• Ajustar niveles mínimos de stock\n• Implementar alertas tempranas",
            "valor_inventario": "💰 Análisis Financiero:\nMonitorear el valor total para optimizar capital de trabajo.\n\nRevisiones sugeridas:\n• Productos de alto valor con baja rotación\n• Oportunidades de negociación con proveedores\n• Balance entre liquidez y disponibilidad\n• Análisis costo-beneficio del inventario",
            "mas_entradas": "📈 Control de Entradas:\nRevisar patrones de abastecimiento para optimizar compras.\n\nRecomendaciones:\n• Verificar si las cantidades corresponden a la demanda\n• Evaluar costos de almacenamiento\n• Negociar mejores términos con proveedores principales\n• Planificar compras basadas en tendencias",
            "mas_salidas": "🏆 Productos Exitosos:\nCapitalizar productos con alta demanda.\n\nEstrategias:\n• Asegurar stock suficiente de productos estrella\n• Negociar mejores precios por volumen\n• Evaluar oportunidades de expansión\n• Mantener niveles óptimos de seguridad",
            "monto_entradas": "📊 Gestión de Compras:\nAnalizar inversión en inventario para optimizar flujo de caja.\n\nAcciones:\n• Revisar términos de pago con proveedores\n• Evaluar frecuencia vs volumen de compra\n• Considerar descuentos por pronto pago\n• Planificar compras según estacionalidad",
            "monto_salidas": "💵 Análisis de Ventas:\nOptimizar ingresos basándose en patrones de salida.\n\nEstrategias:\n• Mantener stock de productos de alto movimiento\n• Evaluar márgenes de productos top\n• Implementar promociones cruzadas\n• Ajustar precios según rotación",
            "sin_movimiento": "💤 Inventario Inactivo:\nAbordar productos sin movimiento para liberar capital.\n\nPlan de acción:\n• Evaluar viabilidad de estos productos\n• Considerar liquidación con descuentos\n• Revisar política de devoluciones a proveedores\n• Replantear mix de productos",
            "variacion_stock": "🔄 Control de Inventario:\nAnalizar variaciones para mejorar planificación.\n\nAcciones de seguimiento:\n• Identificar patrones de consumo\n• Ajustar puntos de reorden\n• Mejorar pronósticos de demanda\n• Optimizar niveles de stock máximo y mínimo",
        }

        return recommendations.get(
            query_type,
            "💡 Recomendación General:\nRevisar datos regularmente para optimizar inventario y mejorar la gestión operativa del stock.",
        )


class InventoryAIService:
    """AI service specialized in intelligent inventory queries and analysis"""

    def __init__(self, config: AIServiceConfig):

        self._config = config
        self._model = None

        if config.api_key and config.api_key != "TU_API_KEY_AQUI":
            self._initialize_ai_model(config.api_key)
            self._config.is_configured = True

        # Specialized context for inventory management
        self._system_prompt = """
        Eres un asistente especializado en gestión y análisis de inventarios.

        CONTEXTO DEL INVENTARIO:
        - responde en 600 caracteres maximo por respuesta
        - Trabajas con insumos farmacéuticos/médicos
        - Cada registro tiene: Código, Descripción, Existencia Inicial (cantidad/costo/monto), Entradas, Salidas y Existencia Final
        - Tu función principal es analizar el movimiento de inventario y dar recomendaciones prácticas
        - Detecta patrones como: sin movimiento, exceso de stock, rotación alta, riesgo de quiebre de stock
        
        FECHA Y HORA DEL SISTEMA: {current_datetime}
        - Úsala como referencia para urgencia de reabastecimiento o vencimiento
        - Calcula impacto en flujo de inventario según esta fecha

        FORMATO DE RESPUESTA:
    
        1. Resumen inicial:
        - Inicia el mensaje con: 
        
        Soy el Asistente de Inventario:
        He analizado tus datos de stock.
        Aquí tienes el resumen:

        - Indica el número total de productos analizados y un resumen breve de hallazgos (ej: “2 productos con stock bajo, 1 sin movimiento”)

        2. Listado:
        - Máximo 10 productos
        - Usa viñetas (•) o números
        - Para cada producto incluye 2-5 datos clave (ej: stock actual, entradas/salidas recientes, valor total, días de cobertura, etc.)
        - Si se dispone de toda la información de un producto, muéstrala completa (existencia inicial, entradas, salidas, existencia final, montos)

        3. Análisis y Recomendación:
        - Explica patrones encontrados: tendencias de movimiento, problemas de stock, oportunidades de mejora
        - Da recomendaciones breves sobre el analisis, accionables y prácticas (ej: “reabastecer en 2 semanas”, “reducir pedidos por baja rotación”)

        REGLAS DE FORMATO:
        - Siempre responde en español
        - No uses tablas grandes
        - Usa listas estilo chat, concisas pero informativas
        - Incluye cifras específicas cuando estén disponibles
        - Enfócate en eficiencia, impacto financiero y decisiones operativas
        """

    def _initialize_ai_model(self, api_key: str) -> None:
        """Initialize Google Gemini AI model"""
        try:
            genai.configure(api_key=api_key)
            # Use model name from configuration to avoid hardcoding
            self._model = genai.GenerativeModel(self._config.model_name)
        except Exception as e:
            print(f"⚠️ AI no disponible: {e}")
            self._config.is_configured = False

    def get_predefined_queries(self) -> Dict[str, InventoryQuery]:
        queries = {
            QueryType.STOCK_BAJO: InventoryQuery(
                query_type=QueryType.STOCK_BAJO,
                title="📉 Stock Bajo",
                icon="📉",
                color="#dc3545",
                description="¿Qué productos tienen stock bajo?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Qué productos tienen stock bajo (5 unidades o menos)?",
            ),
            QueryType.SIN_STOCK: InventoryQuery(
                query_type=QueryType.SIN_STOCK,
                title="❌ Sin Stock",
                icon="❌",
                color="#721c24",
                description="¿Qué productos están agotados?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Qué productos están completamente agotados?",
            ),
            QueryType.VALOR_INVENTARIO: InventoryQuery(
                query_type=QueryType.VALOR_INVENTARIO,
                title="💰 Valor Inventario",
                icon="💰",
                color="#3498db",
                description="¿Cuál es el valor total del inventario?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Cuál es el valor total actual del inventario y cuáles son los productos más valiosos?",
            ),
            QueryType.MAS_ENTRADAS: InventoryQuery(
                query_type=QueryType.MAS_ENTRADAS,
                title="⏰ Más Entradas",
                icon="⏰",
                color="#28a745",
                description="¿Qué productos tuvieron más entradas?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Qué productos tuvieron más entradas de mercancía?",
            ),
            QueryType.MAS_SALIDAS: InventoryQuery(
                query_type=QueryType.MAS_SALIDAS,
                title="🏆 Más Salidas",
                icon="🏆",
                color="#fd7e14",
                description="¿Qué productos tuvieron más salidas?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Qué productos tuvieron más salidas (ventas)?",
            ),
            QueryType.MONTO_ENTRADAS: InventoryQuery(
                query_type=QueryType.MONTO_ENTRADAS,
                title="📦 Monto Entradas",
                icon="📦",
                color="#17a2b8",
                description="¿Cuál es el monto total de entradas?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Cuál es el monto total de entradas y cuáles fueron las mayores?",
            ),
            QueryType.MONTO_SALIDAS: InventoryQuery(
                query_type=QueryType.MONTO_SALIDAS,
                title="🚚 Monto Salidas",
                icon="🚚",
                color="#6f42c1",
                description="¿Cuál es el monto total de salidas?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Cuál es el monto total de salidas y cuáles fueron las mayores?",
            ),
            QueryType.SIN_MOVIMIENTO: InventoryQuery(
                query_type=QueryType.SIN_MOVIMIENTO,
                title="💤 Sin Movimiento",
                icon="💤",
                color="#6c757d",
                description="¿Qué productos no tuvieron movimientos?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Qué productos no tuvieron movimientos (sin entradas ni salidas)?",
            ),
            QueryType.VARIACION_STOCK: InventoryQuery(
                query_type=QueryType.VARIACION_STOCK,
                title="🔄 Variación Stock",
                icon="🔄",
                color="#e83e8c",
                description="¿Cuál fue la variación de stock?",
                sql_query="",  # Handled by InventoryQueries
                user_prompt="¿Cuál fue la variación de stock de los productos?",
            ),
        }

        return {q.query_type.value: q for q in queries.values()}

    def execute_sql_query(self, sql_query: str) -> List[Dict]:
        """
        DEPRECATED: Use InventoryQueries methods instead
        Kept for backwards compatibility

        Args:
            sql_query: SQL query to execute (ignored)

        Returns:
            Empty list - use InventoryQueries instead
        """
        return []

    def generate_ai_response(
        self, user_prompt: str, data: List[Dict], query_type: str = "general"
    ) -> str:
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
        formatted_system_prompt = self._system_prompt.format(
            current_datetime=current_datetime
        )

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

    def _generate_fallback_response(
        self, data: List[Dict], user_prompt: str, query_type: str = "general"
    ) -> str:
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

    # Public explicit local response generator (separate from AI path)
    def generate_local_response(
        self, data: List[Dict], user_prompt: str, query_type: str = "general"
    ) -> str:
        try:
            return ResponseFormatter.format(data, user_prompt, query_type)
        except Exception as e:
            # Defensive: return minimal info if formatting fails unexpectedly
            return f"Asistente de Inventario:\nHe analizado tus datos de stock. Aquí tienes el resumen:\n\n❌ Error formateando respuesta local: {e}"

    def search_specific_product(self, search_term: str) -> QueryResult:
        """Search for a specific product by Código (business code) or description using InventoryQueries"""
        start_time = time.time()

        try:
            search_term = search_term.strip()

            if not search_term:
                return QueryResult(
                    success=False,
                    data=[],
                    error_message="❌ Debe ingresar un Código o descripción de producto",
                )

            sql_data = InventoryQueries.search_product(search_term)

            if not sql_data:
                return QueryResult(
                    success=False,
                    data=[],
                    error_message=f"❌ No se encontró ningún producto con '{search_term}'",
                )

            # Prefer AI response when configured; fallback to local detailed response
            try:
                if self._config.is_configured and self._model is not None:
                    user_prompt = (
                        f"Consulta de producto: '{search_term}'. "
                        "Devuelve una ficha clara con stock actual, movimientos "
                        "(inicial/entradas/salidas/final) y recomendaciones prácticas."
                    )
                    ai_response = self.generate_ai_response(user_prompt, sql_data, "general")
                else:
                    ai_response = self._generate_product_detail_response(sql_data, search_term)
            except Exception:
                ai_response = self._generate_product_detail_response(sql_data, search_term)
            execution_time = time.time() - start_time

            return QueryResult(
                success=True,
                data=sql_data,
                ai_response=ai_response,
                execution_time=execution_time,
            )

        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                error_message=f"❌ Error buscando producto: {str(e)}",
                execution_time=time.time() - start_time,
            )

    def _generate_product_detail_response(
        self, data: List[Dict], search_term: str
    ) -> str:
        """
        Generate detailed product information response

        Args:
            data: Product data from database
            search_term: Original search term

        Returns:
            Formatted product detail response
        """
        if not data:
            return f"❌ No se encontraron productos para '{search_term}'"

        if len(data) == 1:
            # Single product - detailed view
            product = data[0]

            response = f"""📋 Ficha Detallada: {product['producto']}

🆔 Código: {product.get('codigo', product.get('id'))}
💰 Costo Unitario: ${product['costo_unitario']:.2f}

📊 Movimientos:
• Existencia inicial: {product['cant_inicial']} unidades (Monto: ${product['monto_inicial']:.2f})
• Entradas: {product['cant_entrada']} unidades (Monto: ${product['monto_entrada']:.2f})
• Salidas: {product['cant_salida']} unidades (Monto: ${product['monto_salida']:.2f})
• Existencia final: {product['cant_final']} unidades (Monto: ${product['monto_final']:.2f})

💡 Recomendación:
{self._get_product_recommendation(product)}"""

        else:
            # Multiple products - summary view
            response = (
                f"📊 Resultados para '{search_term}': {len(data)} producto(s)\n\n"
            )

            for i, product in enumerate(data, 1):
                status = "✅ Disponible" if product["cant_final"] > 0 else "❌ Agotado"
                code = product.get("codigo", product.get("id"))
                response += f"• {product['producto']} (Código: {code})\n  Stock: {product['cant_final']} unidades - {status}\n\n"

            response += (
                "💡 Tip: Busca por Código específico para ver detalles completos"
            )

        return response

    def _get_product_recommendation(self, product: Dict[str, Any]) -> str:
        """
        Generate specific recommendation for a single product based on inventory data

        Args:
            product: Product data dictionary

        Returns:
            Recommendation string
        """
        cant_final = product.get("cant_final", 0)
        cant_inicial = product.get("cant_inicial", 0)
        cant_entrada = product.get("cant_entrada", 0)
        cant_salida = product.get("cant_salida", 0)

        # Calculate movement patterns
        has_entries = cant_entrada > 0
        has_exits = cant_salida > 0
        stock_change = cant_final - cant_inicial

        # Generate specific recommendation based on product status
        if cant_final == 0:
            if has_exits and not has_entries:
                return "Este producto está completamente agotado y tuvo salidas sin reposición. Considera realizar una compra urgente si es un producto de alta demanda."
            elif not has_entries and not has_exits:
                return "Producto sin movimiento y sin stock. Evalúa si debe mantenerse en inventario o descatalogarse."
            else:
                return "Producto agotado. Revisa la demanda histórica y programa reposición según necesidades."

        elif cant_final <= 3:
            return f"Stock crítico ({cant_final} unidades). Programa reposición inmediata para evitar desabastecimiento."

        elif cant_final <= 10:
            if has_exits:
                return f"Stock bajo ({cant_final} unidades) con movimiento activo. Programa reposición en los próximos días."
            else:
                return f"Stock bajo ({cant_final} unidades) sin movimiento reciente. Monitorea demanda antes de reponer."

        elif stock_change > 0 and has_exits:
            return f"Producto con buen movimiento (stock aumentó en {stock_change} unidades). Mantén niveles óptimos de inventario."

        elif not has_entries and not has_exits:
            return f"Producto sin movimiento con {cant_final} unidades en stock. Considera estrategias para rotarlo o evaluar su continuidad."

        elif has_entries and not has_exits:
            return f"Producto con entradas recientes pero sin salidas. Implementa estrategias de promoción o verifica demanda del mercado."

        else:
            return f"Producto con stock estable ({cant_final} unidades). Mantén monitoreo regular y ajusta según patrones de demanda."

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
                    success=False, data=[], error_message="❌ Consulta no encontrada"
                )

            query = queries[query_key]

            # Get data using centralized queries
            sql_data = InventoryQueries.get_query_data(query_key)

            # 2. Generate AI response with query type for smart formatting
            ai_response = self.generate_ai_response(
                query.user_prompt, sql_data, query_key
            )

            execution_time = time.time() - start_time

            return QueryResult(
                success=True,
                data=sql_data,
                ai_response=ai_response,
                execution_time=execution_time,
            )

        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                error_message=f"❌ Error procesando consulta: {str(e)}",
                execution_time=time.time() - start_time,
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
            "database_mode": "real_data",
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
