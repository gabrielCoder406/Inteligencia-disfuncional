-- =============================================================================
-- SCRIPT DDL: BASE DE DATOS PARA LA GESTIÓN DE CLUB DEPORTIVO
-- Proyecto: Sistema de Gestión Administrativa y Deportiva
-- Grupo: Inteligencia Disfuncional
-- =============================================================================

CREATE DATABASE IF NOT EXISTS bd_club_deportivo;
USE bd_club_deportivo;

-- -----------------------------------------------------------------------------
-- 1. TABLA: CATEGORIA
-- Clasificación deportiva a la que se asignan los jugadores según su edad o nivel.
-- -----------------------------------------------------------------------------
CREATE TABLE CATEGORIA (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL UNIQUE
);

-- -----------------------------------------------------------------------------
-- 2. TABLA: ADMINISTRADOR
-- Personal encargado de gestionar a los jugadores y de revisar los pagos registrados.
-- -----------------------------------------------------------------------------
CREATE TABLE ADMINISTRADOR (
    id_administrador INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 3. TABLA: JUGADOR
-- Miembros del club que visualizan estados de cuenta y cuyos datos deportivos son administrados.
-- -----------------------------------------------------------------------------
CREATE TABLE JUGADOR (
    dni VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    correo_electronico VARCHAR(100) NOT NULL UNIQUE,
    es_federado BOOLEAN NOT NULL DEFAULT FALSE,
    estado_deportivo VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado_deportivo IN ('Activo', 'Baja', 'Lesionado')),
    id_categoria INT NOT NULL,
    id_administrador INT NOT NULL,
    CONSTRAINT fk_jugador_categoria FOREIGN KEY (id_categoria)
        REFERENCES CATEGORIA(id_categoria)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_jugador_administrador FOREIGN KEY (id_administrador)
        REFERENCES ADMINISTRADOR(id_administrador)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- -----------------------------------------------------------------------------
-- 4. TABLA: CUOTA
-- Obligaciones arancelarias mensuales generadas de manera obligatoria para cada deportista.
-- -----------------------------------------------------------------------------
CREATE TABLE CUOTA (
    id_cuota INT AUTO_INCREMENT PRIMARY KEY,
    mes VARCHAR(15) NOT NULL,
    monto DECIMAL(10,2) NOT NULL CHECK (monto > 0),
    dni_jugador VARCHAR(20) NOT NULL,
    CONSTRAINT fk_cuota_jugador FOREIGN KEY (dni_jugador)
        REFERENCES JUGADOR(dni)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- -----------------------------------------------------------------------------
-- 5. TABLA: PAGO
-- Registro individualizado de los ingresos monetarios percibidos por la institución.
-- -----------------------------------------------------------------------------
CREATE TABLE PAGO (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    monto DECIMAL(10,2) NOT NULL CHECK (monto > 0),
    comprobante VARCHAR(255) NULL,
    id_cuota INT NOT NULL,
    id_administrador INT NOT NULL,
    CONSTRAINT fk_pago_cuota FOREIGN KEY (id_cuota)
        REFERENCES CUOTA(id_cuota)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_pago_administrador FOREIGN KEY (id_administrador)
        REFERENCES ADMINISTRADOR(id_administrador)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
