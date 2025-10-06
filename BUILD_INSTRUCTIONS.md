# 📦 Instrucciones para Crear Ejecutable Portable

## Sistema de Inventario - Fundación Salud

Este documento explica cómo compilar la aplicación en un ejecutable portable (.exe para Windows o .app para macOS).

---

## 🎯 Requisitos Previos

1. **Python 3.11+** instalado
2. **Entorno virtual activado** con todas las dependencias
3. **PyInstaller** instalado (se instala automáticamente si falta)

---

## 🚀 Compilación Rápida

### En macOS/Linux:

```bash
./build.sh
```

### En Windows:

```cmd
build.bat
```

---

## 📋 Pasos Detallados

### 1. Preparar el Entorno

```bash
# Activar entorno virtual
source /Users/dmrodriguez/TDR/Entorno/bin/activate  # macOS/Linux
# o
Entorno\Scripts\activate  # Windows

# Instalar dependencias (si no están instaladas)
pip install -r requirements.txt
```

### 2. Migrar Datos a SQLite (Solo Primera Vez)

Si tienes datos en MySQL que quieres migrar:

```bash
python migrate_to_sqlite.py
```

Este script:
- ✅ Conecta a MySQL y lee todos los datos
- ✅ Crea base de datos SQLite portable
- ✅ Migra usuarios, inventario, categorías, etc.
- ✅ Verifica que todo se migró correctamente

### 3. Compilar el Ejecutable

#### Opción A: Script Automatizado (Recomendado)

**macOS/Linux:**
```bash
./build.sh
```

**Windows:**
```cmd
build.bat
```

#### Opción B: Manual con PyInstaller

```bash
pyinstaller build_portable.spec --clean --noconfirm
```

### 4. Encontrar el Ejecutable

Después de la compilación exitosa:

- **Windows:** `dist/FundaSalud.exe`
- **macOS:** `dist/FundaSalud.app` o `dist/FundaSalud`
- **Linux:** `dist/FundaSalud`

---

## 📁 Estructura del Ejecutable

```
dist/
├── FundaSalud.exe          # Ejecutable principal
└── (archivos embebidos internamente)
```

Al ejecutar por primera vez, se creará:

```
FundaSalud.exe
data/                        # Carpeta creada automáticamente
└── sistema_inventario.db   # Base de datos SQLite
```

---

## ✅ Verificación

### Probar el Ejecutable

1. **Navega a la carpeta `dist/`**
2. **Ejecuta el archivo:**
   - Windows: Doble clic en `FundaSalud.exe`
   - macOS: Doble clic en `FundaSalud.app`
   - Linux: `./FundaSalud`

3. **Primera ejecución:**
   - Se creará automáticamente la carpeta `data/`
   - Se creará la base de datos SQLite con estructura completa
   - Se creará un usuario admin por defecto

4. **Login por defecto:**
   - Usuario: `admin`
   - Contraseña: `admin123`

---

## 🔧 Solución de Problemas

### Error: "PyInstaller no encontrado"

```bash
pip install pyinstaller>=6.0.0
```

### Error: "No se puede encontrar logo.png"

Verifica que existe el archivo:
```bash
ls img/logo.png
```

### Error: "Módulo no encontrado"

Instala todas las dependencias:
```bash
pip install -r requirements.txt
```

### Antivirus bloquea el .exe (Windows)

Esto es un **falso positivo** común con PyInstaller. Opciones:

1. **Agregar excepción** en tu antivirus para la carpeta `dist/`
2. **Firmar digitalmente** el ejecutable (requiere certificado)
3. **Distribuir con un instalador** reconocido

### El ejecutable es muy grande (>100 MB)

Esto es normal. Incluye:
- Python runtime completo
- Todas las librerías (customtkinter, Pillow, etc.)
- Recursos embebidos

Para reducir tamaño:
- Excluir módulos no usados en `build_portable.spec`
- Usar UPX para comprimir (ya habilitado)

---

## 📦 Distribución

### Qué Distribuir

**Opción 1: Solo el Ejecutable (Recomendado)**
```
FundaSalud.exe
```
- La BD se crea automáticamente en primera ejecución
- Usuario admin por defecto

**Opción 2: Con Base de Datos Pre-poblada**
```
FundaSalud.exe
data/
└── sistema_inventario.db
```
- Incluye datos existentes
- No requiere configuración inicial

**Opción 3: Paquete Completo**
```
FundaSalud/
├── FundaSalud.exe
├── data/
│   └── sistema_inventario.db
└── README.txt
```

### Crear ZIP para Distribución

**Windows:**
```cmd
cd dist
tar -a -c -f FundaSalud-v1.0.0.zip FundaSalud.exe
```

**macOS/Linux:**
```bash
cd dist
zip -r FundaSalud-v1.0.0.zip FundaSalud.app
```

---

## 🔐 Configuración de API Keys

Si usas Google Gemini AI, necesitarás configurar la API key:

1. Crear archivo `config.ini` junto al ejecutable:

```ini
[API]
GEMINI_API_KEY = tu_api_key_aqui
```

2. O configurar variable de entorno:

**Windows:**
```cmd
setx GEMINI_API_KEY "tu_api_key_aqui"
```

**macOS/Linux:**
```bash
export GEMINI_API_KEY="tu_api_key_aqui"
```

---

## 📊 Tamaño Esperado

- **Windows:** ~80-120 MB
- **macOS:** ~90-130 MB
- **Linux:** ~85-125 MB

El tamaño varía según:
- Sistema operativo
- Dependencias incluidas
- Nivel de compresión UPX

---

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa los logs** de compilación
2. **Verifica dependencias:** `pip list`
3. **Limpia y recompila:** 
   ```bash
   rm -rf build/ dist/
   ./build.sh
   ```

---

## 📝 Notas Importantes

### ✅ Ventajas del Ejecutable Portable

- ✅ No requiere Python instalado
- ✅ No requiere MySQL instalado
- ✅ Base de datos embebida (SQLite)
- ✅ Todos los recursos incluidos
- ✅ Fácil de distribuir
- ✅ Funciona offline (excepto AI)

### ⚠️ Limitaciones

- ⚠️ Tamaño grande (~100 MB)
- ⚠️ Puede tardar 5-10 segundos en iniciar
- ⚠️ Algunos antivirus pueden dar falso positivo
- ⚠️ AI requiere conexión a internet

---

## 🔄 Actualizar el Ejecutable

Para crear una nueva versión:

1. Hacer cambios en el código fuente
2. Actualizar versión en `config.py`
3. Recompilar:
   ```bash
   ./build.sh  # o build.bat
   ```
4. Distribuir nuevo ejecutable

---

## 📄 Licencia

Sistema de Inventario - Fundación Salud
Versión 1.0.0

---

**¿Necesitas ayuda?** Contacta al equipo de desarrollo.
