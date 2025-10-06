#!/bin/bash
# Script de compilación para macOS/Linux
# Sistema de Inventario - Fundación Salud

echo "============================================================"
echo "🔨 COMPILANDO EJECUTABLE PORTABLE - FundaSalud"
echo "============================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: main.py no encontrado${NC}"
    echo "Por favor ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar que PyInstaller está instalado
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}⚠️  PyInstaller no encontrado, instalando...${NC}"
    pip install pyinstaller>=6.0.0
fi

# Limpiar builds anteriores
echo -e "${YELLOW}🧹 Limpiando builds anteriores...${NC}"
rm -rf build/ dist/ __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Compilar con PyInstaller
echo -e "${GREEN}🔨 Compilando ejecutable...${NC}"
pyinstaller build_portable.spec --clean --noconfirm

# Verificar si la compilación fue exitosa
if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo -e "${GREEN}✅ COMPILACIÓN EXITOSA${NC}"
    echo "============================================================"
    echo ""
    
    # Mostrar información del ejecutable
    if [ -f "dist/FundaSalud" ]; then
        echo -e "${GREEN}📦 Ejecutable creado:${NC} dist/FundaSalud"
        ls -lh dist/FundaSalud
    elif [ -d "dist/FundaSalud.app" ]; then
        echo -e "${GREEN}📦 App bundle creada:${NC} dist/FundaSalud.app"
        ls -lh dist/FundaSalud.app
    fi
    
    echo ""
    echo -e "${YELLOW}📝 Notas importantes:${NC}"
    echo "  1. El ejecutable está en la carpeta 'dist/'"
    echo "  2. La primera vez que lo ejecutes, creará una carpeta 'data/' para la BD"
    echo "  3. Puedes distribuir el ejecutable sin dependencias adicionales"
    echo ""
    echo "============================================================"
else
    echo ""
    echo "============================================================"
    echo -e "${RED}❌ ERROR EN LA COMPILACIÓN${NC}"
    echo "============================================================"
    echo "Revisa los errores arriba para más detalles"
    exit 1
fi
