-- -- Crear base de datos
CREATE DATABASE IF NOT EXISTS sistema_inventario;
USE sistema_inventario;

-- Crear tabla 'personal'
CREATE TABLE IF NOT EXISTS personal (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    tiempo INT,
    contrasena VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
);

-- -----------------------------------------------------------------------------

-- la tabla padre
CREATE TABLE IF NOT EXISTS Inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descripcion_insumo VARCHAR(255),
    tipo VARCHAR(25),
    cantidad INT,
    costo_unitario DECIMAL(10, 2),
    monto_total DECIMAL(10, 2)
);

    -- Crear la tabla hija
    CREATE TABLE IF NOT EXISTS existencia_inicial (
        id INT AUTO_INCREMENT PRIMARY KEY,
        inventario_id INT, -- Clave foránea para referenciar a Inventario
        nombre varchar(50),
        FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
    );

    -- Crear la tabla hija
    CREATE TABLE IF NOT EXISTS entradas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        inventario_id INT, -- Clave foránea para referenciar a Inventario
        nombre varchar(50),
        FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
    );

    -- Crear la tabla hija
    CREATE TABLE IF NOT EXISTS salidas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        inventario_id INT, -- Clave foránea para referenciar a Inventario
        nombre varchar(50),
        FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
    );

    -- Crear la tabla hija
    CREATE TABLE IF NOT EXISTS existencia_final (
        id INT AUTO_INCREMENT PRIMARY KEY,
        inventario_id INT, -- Clave foránea para referenciar a Inventario
        nombre varchar(50),
        FOREIGN KEY (inventario_id) REFERENCES Inventario(id)
    );

-- -----------------------------------------------------------------------------

