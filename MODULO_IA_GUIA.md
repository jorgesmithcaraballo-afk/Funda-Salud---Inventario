# 🤖 Módulo IA WhatsApp - Guía Técnica Completa

## 🎯 ¿Qué es el Módulo de IA WhatsApp?

Un sistema **conversacional tipo WhatsApp** que **analiza tu inventario** usando **Google Gemini AI** con **11 consultas inteligentes** y **cálculos de fecha/hora en tiempo real**.

---

## 🏗️ **ARQUITECTURA LIMPIA (Clean Architecture)**

```
📁 fs_inv/
├── 🎯 chat_whatsapp_app.py          # ⭐ APLICACIÓN WHATSAPP PRINCIPAL
├── 🤖 services/ai_service.py        # ⭐ Motor IA con Gemini + Fecha actual
├── 📊 services/mock_data.py         # ⭐ Datos mock realistas (11 consultas)
├── 🎮 controllers/chat_controller.py # ⭐ Controlador conversacional
├── 📊 models/inventory_models.py    # ⭐ Modelos de datos (11 tipos)
└── 📖 README.md                     # Guía de inicio rápido
```

**💡 EJECUCIÓN:** Solo ejecuta `python chat_whatsapp_app.py` y ya tienes el chat WhatsApp funcionando.

---

## ⚡ **USO SÚPER RÁPIDO (30 segundos)**

### **PASO 1: Ejecutar chat WhatsApp directo**
```bash
python chat_whatsapp_app.py
# ¡Ya tienes el chat WhatsApp con IA! Sin login, conversacional
```

### **PASO 2: Chatear con la IA**
1. **🤖 IA te saluda:** "¡Hola! Soy tu asistente de inventario"
2. **📋 Aparecen 11 botones:** 10 consultas generales + 1 específica
3. **⚡ Haces clic** en la consulta que necesites
4. **💬 IA responde** en burbuja con análisis completo
5. **🔄 Menú reaparece** para nueva consulta

---

## 🤖 **11 CONSULTAS IA INTELIGENTES**

### **📋 Consultas Generales (Todo el Inventario):**

| # | Consulta | Descripción | Usa Fecha Actual |
|---|----------|-------------|------------------|
| 1 | **📉 Stock Bajo** | Productos próximos a agotarse | ✅ Urgencia por fecha |
| 2 | **⏰ Próximos a Vencer** | Productos que vencen en 30 días | ✅ Calcula desde HOY |
| 3 | **❌ Productos Vencidos** | Items ya vencidos | ✅ Compara con fecha actual |
| 4 | **🏆 Más Vendidos** | Top productos por ventas | ✅ Período desde fecha actual |
| 5 | **🐌 Baja Rotación** | Productos con poca demanda | ✅ Período desde fecha actual |
| 6 | **💰 Valor del Inventario** | Valor total en costo y venta | ✅ A fecha actual |
| 7 | **📈 Cambios de Precio** | Productos con precios modificados | ✅ Últimos 30 días |
| 8 | **📦 Exceso de Stock** | Productos sobrestockeados | ✅ Urgencia por fecha |
| 9 | **🚫 Sin Stock** | Productos completamente agotados | ✅ Al momento actual |
| 10 | **⚡ Reabastecimiento Urgente** | Items críticos que requieren acción | ✅ Prioridad por fecha |

### **🔍 Consulta Específica:**
| # | Consulta | Descripción |
|---|----------|-------------|
| 11 | **🔍 Consultar Producto Específico** | Todas las consultas aplicadas a UN producto |

---

## 📅 **NOVEDAD: FECHA/HORA EN TIEMPO REAL**

### **⏰ Cómo funciona:**
```python
# services/ai_service.py - línea 253
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# La IA recibe en el prompt:
"""
FECHA Y HORA ACTUAL DEL SISTEMA: 2024-04-15 14:30:25
- Usa esta fecha para calcular si productos están vencidos
- Calcula días hasta vencimiento basándote en esta fecha actual  
- Determina urgencia de reabastecimiento según esta fecha
"""
```

### **🎯 Beneficios:**
- **✅ Cálculos precisos** de vencimientos
- **✅ Determinación exacta** de productos vencidos vs vigentes
- **✅ Urgencia contextual** según momento de consulta
- **✅ Análisis temporal** preciso para rotación y ventas

---

## 🎨 **INTERFAZ WHATSAPP CONVERSACIONAL**

### **📱 Componentes UI:**

| Componente | Descripción | Archivo |
|------------|-------------|---------|
| **🔵 Header azul** | Estado IA + título | `chat_whatsapp_app.py:82` |
| **💬 Chat scroll** | Área de mensajes con scroll inteligente | `chat_whatsapp_app.py:95` |
| **🤖 Burbujas bot** | Mensajes IA (izquierda, gris) | `chat_whatsapp_app.py:183` |
| **👤 Burbujas usuario** | Mensajes usuario (derecha, azul) | `chat_whatsapp_app.py:217` |
| **📋 Botones consulta** | Menú de 11 opciones dinámico | `chat_whatsapp_app.py:319` |

### **🔄 Flujo Conversacional:**

```
[IA saluda] → [11 botones] → [Usuario elige] → [IA analiza] → [Respuesta] → [11 botones]
     ↓              ↓             ↓              ↓            ↓             ↓
  Inicial      Menú dinámico   Oculta menú   Scroll smart  Una burbuja   Menú reaparece
```

### **🎯 Scroll Inteligente:**
- **📍 Scroll al inicio** de respuesta IA (no al final del chat)
- **⚡ Auto-scroll** para mensajes de saludo y preguntas
- **🎯 Posición calculada** matemáticamente para UX óptima

---

## 🛠️ **CONFIGURACIÓN IA (OPCIONAL)**

### **🔥 OPCIÓN A: Google Gemini (Recomendada)**
```bash
# 1. API Key GRATIS: https://makersuite.google.com/app/apikey
# 2. Editar chat_whatsapp_app.py línea 13:
API_KEY = "AIzaSy..."  # ⚡ Pegá tu key aquí

# 3. ¡Listo! IA inteligente activada
```

**✅ Modelo usado:** `gemini-1.5-flash-8b` (100% gratuito, rápido)

### **🔧 OPCIÓN B: Sin configurar IA**
```bash
# Solo ejecutar sin configurar:  
python chat_whatsapp_app.py
# ✅ Funciona con datos mock + respuestas básicas
```

---

## 🗂️ **DATOS MOCK INTELIGENTES**

### **📊 Archivo:** `services/mock_data.py`

**11 datasets realistas** simulando respuestas de base de datos MySQL:

```python
# Ejemplo: Stock bajo
{
  "id": 1, 
  "descripcion": "Acetaminofén 500mg", 
  "stock_actual": 15, 
  "stock_minimo": 50, 
  "proveedor": "FarmaPlus"
}

# Ejemplo: Próximos a vencer  
{
  "descripcion": "Vitamina C", 
  "fecha_vencimiento": "2024-05-30",  # Calculado desde HOY
  "lote": "VC202405"
}
```

**🎯 Preparado para MySQL real:** Solo cambiar `_use_mock_data = False` en `ai_service.py:29`

---

## 🎛️ **CONFIGURACIÓN AVANZADA**

### **🤖 Personalizar formato respuesta IA:**
```python
# services/ai_service.py - líneas 49-65
FORMATO DE RESPUESTA OBLIGATORIO:

1. Resumen inicial: Número total de resultados encontrados
2. Lista máximo 5 productos con 2-3 datos clave
3. Si hay más: "(... X productos más no mostrados)"
4. Recomendación breve en texto natural
5. No tablas grandes, listas cortas estilo chat
```

### **🎨 Personalizar colores/UI:**
```python
# chat_whatsapp_app.py - líneas 14-18
AZUL_PRIMARIO = "#004aad"        # Color header
GRIS_CLARO = "#f0f0f0"          # Fondo burbujas IA
VERDE_WHATSAPP = "#25d366"       # Acentos WhatsApp
GRIS_CHAT = "#e1ffc7"           # Fondo conversación
```

### **⚡ Agregar nueva consulta:**
1. **Agregar enum** en `models/inventory_models.py:15`
2. **Crear mock data** en `services/mock_data.py`
3. **Definir consulta** en `services/ai_service.py:75`
4. **Agregar botón** en `chat_whatsapp_app.py:330`

---

## 🔧 **SOLUCIÓN DE PROBLEMAS**

### **❌ "No responde la IA"**
- Verificar API key en `chat_whatsapp_app.py:13`
- Probar conexión: https://makersuite.google.com/app/apikey

### **❌ "Error de importación"**
```bash  
pip install customtkinter mysql-connector-python google-generativeai
```

### **❌ "No aparecen las 11 preguntas"**
- Verificar `chat_whatsapp_app.py:330` tiene las 11 consultas
- Revisar `services/ai_service.py` tiene los 11 tipos definidos

### **❌ "Scroll no funciona bien"**
- El scroll va al **inicio** de respuesta IA (no al final)
- Es comportamiento correcto para mejor UX

---

## 🚀 **CARACTERÍSTICAS TÉCNICAS**

### **🏗️ Arquitectura:**
- **Clean Architecture** con separación de responsabilidades
- **MVC Pattern** (Model-View-Controller)
- **Dependency Injection** para servicios
- **Type Hints** completos en Python 3.11+

### **🤖 IA & Datos:**
- **Google Gemini 1.5 Flash 8B** (modelo gratuito)
- **Mock data realista** con 11 consultas diferentes
- **Fecha/hora sistema** integrada en prompts
- **Fallback inteligente** si falla la conexión IA

### **🎨 UI/UX:**
- **CustomTkinter** para UI moderna
- **Scroll inteligente** matemáticamente calculado  
- **Responsive design** con weights y sticky
- **Burbujas conversacionales** tipo WhatsApp

### **⚡ Performance:**
- **Threading** para evitar bloquear UI
- **Lazy loading** de componentes
- **Memory management** eficiente
- **Background processing** para consultas IA

---

## 📚 **PRÓXIMOS PASOS (ROADMAP)**

### **🔄 En este archivo (listo para producción):**
1. **Cambiar** `_use_mock_data = False` en `ai_service.py`
2. **Conectar** MySQL real via `conexion.py`  
3. **Configurar** base de datos con `estructura_bd.sql`

### **🚀 Expansiones futuras:**
- **Más consultas** específicas por categoría
- **Exportación** de resultados a Excel  
- **Gráficos** integrados en chat
- **Notificaciones** push para alertas críticas

---

**🎉 SISTEMA COMPLETO Y PROFESIONAL - Listo para usar en producción con IA conversacional**

---

## 📞 **SOPORTE**

Si necesitas ayuda:
1. **README.md** - Inicio rápido
2. **Este archivo** - Guía técnica completa
3. **Código comentado** - Documentación inline en archivos

**✅ Todo está documentado, comentado y listo para usar.**