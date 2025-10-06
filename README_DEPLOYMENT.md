# 🚀 Guía de Despliegue - FundaSalud

## Sistema de Inventario - Fundación Salud

---

## 📋 **RESUMEN**

Este documento explica cómo crear un ejecutable de FundaSalud para Windows que funcione con MySQL.

**Enfoque Elegido:** MySQL Tradicional (No Embebido)
- ✅ Código estable y probado
- ✅ Sin riesgos de bugs
- ✅ Fácil de mantener
- ✅ Instalación profesional

---

## 🎯 **PROCESO COMPLETO**

### **EN MAC (Desarrollo)**

#### 1. **Preparar el Proyecto**
```bash
# Ya está listo ✅
# - Código funcionando
# - MySQL configurado
# - Dependencias instaladas
```

#### 2. **Archivos Creados para Windows**
- ✅ `build.bat` - Script de compilación
- ✅ `setup_mysql_windows.bat` - Configuración de MySQL
- ✅ `INSTALACION_WINDOWS.md` - Guía completa
- ✅ `build_portable.spec` - Configuración PyInstaller

#### 3. **Transferir a Windows**
```bash
# Comprimir proyecto
zip -r FundaSalud-Source.zip . -x "venv/*" -x "dist/*" -x "build/*" -x "__pycache__/*"

# Transferir a Windows por:
# - USB
# - Email
# - Google Drive
# - GitHub
```

---

### **EN WINDOWS (Compilación)**

#### 1. **Preparar Entorno**

```cmd
# Instalar Python 3.11+
# Descargar de: https://www.python.org/downloads/
# ✅ Marcar "Add Python to PATH"

# Descomprimir proyecto
# Abrir CMD en la carpeta del proyecto

# Instalar dependencias
pip install -r requirements.txt
```

#### 2. **Instalar y Configurar MySQL**

```cmd
# Opción A: Instalador MySQL
# 1. Descargar de: https://dev.mysql.com/downloads/mysql/
# 2. Ejecutar instalador
# 3. Configurar password root

# Opción B: Chocolatey
choco install mysql

# Configurar base de datos
setup_mysql_windows.bat
```

#### 3. **Compilar Ejecutable**

```cmd
# Ejecutar script de compilación
build.bat

# Resultado: dist\FundaSalud.exe
```

#### 4. **Probar Ejecutable**

```cmd
cd dist
FundaSalud.exe

# Verificar:
# - Inicia correctamente
# - Se conecta a MySQL
# - Login funciona
# - Todas las pantallas funcionan
```

---

## 📦 **DISTRIBUCIÓN**

### **Opción 1: Ejecutable + Instrucciones**

Crear un paquete con:
```
FundaSalud-v1.0/
├── FundaSalud.exe
├── setup_mysql_windows.bat
├── INSTALACION_WINDOWS.md
└── database/
    └── estructura_bd.sql
```

**Instrucciones para el usuario:**
1. Instalar MySQL (si no lo tiene)
2. Ejecutar `setup_mysql_windows.bat`
3. Ejecutar `FundaSalud.exe`

---

### **Opción 2: Instalador Profesional (Recomendado)**

Usar **Inno Setup** para crear un instalador que:

1. **Detecta MySQL**
   - Si no está → ofrece instalarlo
   - Si está → verifica versión

2. **Instala FundaSalud**
   - Copia archivos a Program Files
   - Crea acceso directo

3. **Configura Base de Datos**
   - Crea BD automáticamente
   - Importa estructura
   - Crea usuario

4. **Finaliza**
   - Ejecuta aplicación
   - Muestra pantalla de bienvenida

**Crear instalador con Inno Setup:**

```pascal
; Script de Inno Setup (FundaSalud-Setup.iss)
[Setup]
AppName=FundaSalud - Sistema de Inventario
AppVersion=1.0.0
DefaultDirName={pf}\FundaSalud
DefaultGroupName=FundaSalud
OutputBaseFilename=FundaSalud-Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\FundaSalud.exe"; DestDir: "{app}"
Source: "database\estructura_bd.sql"; DestDir: "{app}\database"
Source: "setup_mysql_windows.bat"; DestDir: "{app}"

[Icons]
Name: "{group}\FundaSalud"; Filename: "{app}\FundaSalud.exe"
Name: "{commondesktop}\FundaSalud"; Filename: "{app}\FundaSalud.exe"

[Run]
Filename: "{app}\setup_mysql_windows.bat"; Description: "Configurar MySQL"; Flags: postinstall
Filename: "{app}\FundaSalud.exe"; Description: "Ejecutar FundaSalud"; Flags: postinstall nowait
```

---

## 🔧 **MANTENIMIENTO**

### **Actualizar la Aplicación**

1. **Hacer cambios en Mac**
   ```bash
   # Modificar código
   # Probar localmente
   git commit -m "Nueva funcionalidad"
   ```

2. **Transferir a Windows**
   ```bash
   # Sincronizar código
   git push
   # O comprimir y transferir
   ```

3. **Recompilar en Windows**
   ```cmd
   build.bat
   ```

4. **Distribuir nueva versión**
   ```cmd
   # Crear nuevo instalador
   # O distribuir nuevo .exe
   ```

---

## 📊 **ESPECIFICACIONES TÉCNICAS**

### **Requisitos del Sistema**
- **OS:** Windows 10 o superior
- **RAM:** 4 GB mínimo
- **Disco:** 500 MB libres
- **MySQL:** 8.0 o superior
- **Python:** 3.11+ (solo para desarrollo)

### **Tamaño de Archivos**
- **FundaSalud.exe:** ~50-80 MB
- **MySQL Installer:** ~400 MB
- **Instalador completo:** ~500 MB

### **Dependencias**
```
customtkinter>=5.2.0
google-generativeai>=0.3.0
mysql-connector-python>=8.0.32
openpyxl>=3.1.0
Pillow>=8.0.0
pyinstaller>=6.0.0
```

---

## ✅ **CHECKLIST DE DESPLIEGUE**

### **Desarrollo (Mac)**
- [x] Código funcionando correctamente
- [x] MySQL configurado
- [x] Scripts de compilación creados
- [x] Documentación completa
- [ ] Transferir a Windows

### **Compilación (Windows)**
- [ ] Python instalado
- [ ] Dependencias instaladas
- [ ] MySQL instalado y configurado
- [ ] Ejecutable compilado
- [ ] Ejecutable probado

### **Distribución**
- [ ] Paquete de distribución creado
- [ ] Instalador creado (opcional)
- [ ] Documentación incluida
- [ ] Probado en máquina limpia

---

## 🆘 **SOPORTE Y TROUBLESHOOTING**

### **Problemas Comunes**

**1. "PyInstaller falla al compilar"**
```cmd
# Limpiar y reintentar
rmdir /s /q build dist
pip install --upgrade pyinstaller
build.bat
```

**2. "MySQL no se conecta"**
```cmd
# Verificar servicio
services.msc
# Buscar "MySQL80" → debe estar "En ejecución"

# Probar conexión
mysql -u fs -pGato7Sol sistema_inventario
```

**3. "Falta customtkinter"**
```cmd
pip install --upgrade customtkinter
```

**4. "Antivirus bloquea .exe"**
```
# Agregar excepción en antivirus
# O firmar digitalmente el ejecutable
```

---

## 📞 **CONTACTO**

Para soporte técnico:
- Revisar `INSTALACION_WINDOWS.md`
- Verificar logs de la aplicación
- Contactar al desarrollador

---

## 🎉 **¡LISTO!**

Siguiendo esta guía, tendrás FundaSalud funcionando en Windows con MySQL de forma profesional y confiable.

**Ventajas de este enfoque:**
- ✅ Código estable (sin cambios riesgosos)
- ✅ MySQL estándar (bien soportado)
- ✅ Fácil de mantener
- ✅ Profesional
- ✅ Escalable

---

**Última actualización:** Octubre 2025  
**Versión:** 1.0.0
