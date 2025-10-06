# 📦 Guía de Instalación para Windows

## Sistema de Inventario - Fundación Salud

---

## 🎯 **PASOS PARA INSTALAR EN WINDOWS**

### **Prerequisitos**
- Windows 10 o superior
- Conexión a internet (solo para instalación inicial)
- Permisos de administrador

---

## 📋 **OPCIÓN 1: Instalación Completa (Recomendado)**

### **Paso 1: Instalar MySQL**

#### **Método A: Instalador Oficial (Recomendado)**

1. **Descargar MySQL Community Server**
   - Ir a: https://dev.mysql.com/downloads/mysql/
   - Seleccionar: "Windows (x86, 64-bit), MSI Installer"
   - Descargar el instalador completo (~400 MB)

2. **Ejecutar el Instalador**
   ```
   - Doble clic en mysql-installer-community-X.X.XX.msi
   - Seleccionar "Developer Default"
   - Click "Next" hasta llegar a "Accounts and Roles"
   ```

3. **Configurar MySQL**
   ```
   En "Accounts and Roles":
   - MySQL Root Password: [elegir una contraseña segura]
   - Confirmar password
   - Click "Next" hasta finalizar
   ```

4. **Verificar Instalación**
   ```cmd
   # Abrir CMD y ejecutar:
   mysql --version
   
   # Debería mostrar: mysql  Ver 8.0.XX
   ```

#### **Método B: Con Chocolatey (Automático)**

```powershell
# Abrir PowerShell como Administrador y ejecutar:
choco install mysql
```

---

### **Paso 2: Configurar Base de Datos**

1. **Ejecutar script de configuración**
   ```cmd
   cd C:\ruta\a\FundaSalud-Entregado
   setup_mysql_windows.bat
   ```

2. **Seguir las instrucciones en pantalla**
   - Ingresar password de root de MySQL
   - El script creará automáticamente:
     - Base de datos `sistema_inventario`
     - Usuario `fs` con password `Gato7Sol`
     - Estructura de tablas

---

### **Paso 3: Compilar Ejecutable**

1. **Instalar Python 3.11 o superior**
   - Descargar de: https://www.python.org/downloads/
   - ✅ Marcar "Add Python to PATH" durante instalación

2. **Instalar dependencias**
   ```cmd
   cd C:\ruta\a\FundaSalud-Entregado
   pip install -r requirements.txt
   ```

3. **Compilar ejecutable**
   ```cmd
   build.bat
   ```

4. **El ejecutable estará en:**
   ```
   dist\FundaSalud.exe
   ```

---

## 📋 **OPCIÓN 2: Solo Ejecutar (Si ya está compilado)**

### **Requisitos:**
1. MySQL instalado y configurado
2. Base de datos `sistema_inventario` creada
3. Usuario `fs` con permisos

### **Ejecutar:**
```cmd
cd dist
FundaSalud.exe
```

---

## 🔧 **SOLUCIÓN DE PROBLEMAS**

### **Error: "MySQL no está instalado"**
```
Solución:
1. Instalar MySQL Community Server
2. Ejecutar setup_mysql_windows.bat
```

### **Error: "No se puede conectar a la base de datos"**
```
Verificar:
1. MySQL está corriendo:
   - Abrir "Servicios" de Windows
   - Buscar "MySQL80"
   - Estado debe ser "En ejecución"

2. Credenciales correctas:
   - Usuario: fs
   - Password: Gato7Sol
   - Base de datos: sistema_inventario
```

### **Error: "PyInstaller no encontrado"**
```cmd
pip install pyinstaller>=6.0.0
```

### **Error: "No se puede importar customtkinter"**
```cmd
pip install -r requirements.txt
```

### **Antivirus bloquea el .exe**
```
Esto es un falso positivo común con PyInstaller.

Solución:
1. Agregar excepción en el antivirus para la carpeta dist\
2. O temporalmente deshabilitar antivirus durante primera ejecución
```

---

## 📊 **ESTRUCTURA DE ARCHIVOS**

```
FundaSalud-Entregado/
├── main.py                      # Código fuente principal
├── requirements.txt             # Dependencias Python
├── build.bat                    # Script de compilación
├── setup_mysql_windows.bat      # Configuración MySQL
├── build_portable.spec          # Configuración PyInstaller
├── database/
│   └── estructura_bd.sql        # Estructura de BD
├── dist/                        # (generado al compilar)
│   └── FundaSalud.exe          # ⭐ Ejecutable final
└── ...
```

---

## 🚀 **INICIO RÁPIDO (Resumen)**

```cmd
# 1. Instalar MySQL
mysql-installer-community-X.X.XX.msi

# 2. Configurar BD
setup_mysql_windows.bat

# 3. Instalar Python y dependencias
pip install -r requirements.txt

# 4. Compilar
build.bat

# 5. Ejecutar
dist\FundaSalud.exe
```

---

## 📝 **NOTAS IMPORTANTES**

1. **Primera Ejecución**
   - Puede tardar 5-10 segundos en iniciar
   - Se conectará a MySQL localhost

2. **Credenciales por Defecto**
   - Usuario: admin
   - Contraseña: admin123

3. **Requisitos del Sistema**
   - Windows 10 o superior
   - 4 GB RAM mínimo
   - 500 MB espacio en disco
   - MySQL 8.0 o superior

4. **Distribución**
   - Para distribuir a otros usuarios:
     - Compartir `FundaSalud.exe`
     - Incluir `setup_mysql_windows.bat`
     - Incluir estas instrucciones

---

## 🆘 **SOPORTE**

Si encuentras problemas:
1. Revisar esta guía completa
2. Verificar que MySQL está corriendo
3. Verificar credenciales de conexión
4. Revisar logs de la aplicación

---

## ✅ **CHECKLIST DE INSTALACIÓN**

- [ ] MySQL instalado
- [ ] MySQL corriendo (servicio activo)
- [ ] Base de datos `sistema_inventario` creada
- [ ] Usuario `fs` creado con permisos
- [ ] Python 3.11+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Ejecutable compilado (`build.bat`)
- [ ] Aplicación probada y funcionando

---

**¡Listo para usar FundaSalud!** 🎉
