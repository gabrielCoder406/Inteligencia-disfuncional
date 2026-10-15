-- =============================================================================
-- SCRIPT DDL v5 (Hito 3 - Integración): BASE DE DATOS DEL CLUB GENERAL PAZ JUNIOR
-- Proyecto: Sistema de Gestión de Pagos e Inscripciones
-- Grupo: Inteligencia Disfuncional - ISPC Módulo Programador 2026 - Comisión B1
-- SGBD: MySQL 8.0 (probado en MySQL 8.0.46)
--
-- Orden de ejecución:
--   1) script_ddl_club_deportivo_v5.sql   (este archivo: tablas, triggers, vistas)
--   2) script_roles_usuarios.sql          (roles de acceso y usuarios del SGBD)
--   3) script_datos_prueba.sql            (datos de prueba)
--
-- Cambios respecto de la v4 (Evidencia 5), todos derivados de las reglas de negocio:
--   * CATEGORIA.monto_cuota        -> el importe depende de la categoría (regla 2).
--   * ADMINISTRADOR.nombre         -> columna "Responsable" (Sección 2, punto 1).
--   * JUGADOR.fecha_nacimiento     -> categorías por edad (regla 6); la pide el ABM.
--   * JUGADOR.contrasena           -> el socio ingresa a su portal con DNI y contraseña.
--   * CUOTA.mes pasa a número 1-12 y se agrega CUOTA.anio (Mes/Anio_Periodo del Hito 1).
--   * CUOTA.fecha_vencimiento y CUOTA.estado_pago ('En mora' / 'Al día') (reglas 2 y 3).
--   * PAGO.medio_pago               -> se registra la modalidad del pago (regla 4).
--   * PAGO.id_cuota UNIQUE          -> relación "Aplica a" 1 a 1.
--   * CUOTA -> JUGADOR pasa de ON DELETE CASCADE a RESTRICT: la baja es lógica y el historial
--     de cuotas no debe perderse.
-- =============================================================================

-- Asegura que los acentos (día, Gómez) se guarden bien en cualquier cliente
SET NAMES utf8mb4;

DROP DATABASE IF EXISTS bd_club_deportivo;
CREATE DATABASE bd_club_deportivo
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;
USE bd_club_deportivo;

-- -----------------------------------------------------------------------------
-- 1. TABLA: CATEGORIA
-- Clasificación deportiva a la que se asignan los jugadores según su edad.
-- -----------------------------------------------------------------------------
CREATE TABLE CATEGORIA (
    id_categoria     INT           AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50)   NOT NULL,
    monto_cuota      DECIMAL(10,2) NOT NULL,
    CONSTRAINT uq_categoria_nombre UNIQUE (nombre_categoria),
    CONSTRAINT ck_categoria_monto  CHECK (monto_cuota > 0)
);

-- -----------------------------------------------------------------------------
-- 2. TABLA: ADMINISTRADOR
-- Personal que gestiona a los jugadores y valida los pagos registrados.
-- -----------------------------------------------------------------------------
CREATE TABLE ADMINISTRADOR (
    id_administrador INT          AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    correo           VARCHAR(100) NOT NULL,
    contrasena       VARCHAR(255) NOT NULL,          -- hash SHA-256, nunca texto plano
    CONSTRAINT uq_admin_correo UNIQUE (correo),
    CONSTRAINT ck_admin_correo CHECK (correo LIKE '%_@_%._%')
);

-- -----------------------------------------------------------------------------
-- 3. TABLA: JUGADOR
-- Socios/deportistas del club. La baja es lógica (estado_deportivo = 'Baja').
-- -----------------------------------------------------------------------------
CREATE TABLE JUGADOR (
    dni                VARCHAR(20)  NOT NULL PRIMARY KEY,
    nombre             VARCHAR(50)  NOT NULL,
    apellido           VARCHAR(50)  NOT NULL,
    fecha_nacimiento   DATE         NOT NULL,
    correo_electronico VARCHAR(100) NOT NULL,
    contrasena         VARCHAR(255) NOT NULL,        -- hash SHA-256 (portal de socios)
    es_federado        BOOLEAN      NOT NULL DEFAULT FALSE,
    estado_deportivo   VARCHAR(20)  NOT NULL DEFAULT 'Activo',
    id_categoria       INT          NOT NULL,
    id_administrador   INT          NOT NULL,
    CONSTRAINT uq_jugador_correo  UNIQUE (correo_electronico),
    CONSTRAINT ck_jugador_dni     CHECK (dni REGEXP '^[0-9]{7,8}$'),
    CONSTRAINT ck_jugador_correo  CHECK (correo_electronico LIKE '%_@_%._%'),
    CONSTRAINT ck_jugador_estado  CHECK (estado_deportivo IN ('Activo', 'Baja', 'Lesionado')),
    CONSTRAINT ck_jugador_fnac    CHECK (fecha_nacimiento >= '1930-01-01'),
    CONSTRAINT fk_jugador_categoria FOREIGN KEY (id_categoria)
        REFERENCES CATEGORIA(id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_jugador_administrador FOREIGN KEY (id_administrador)
        REFERENCES ADMINISTRADOR(id_administrador)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- -----------------------------------------------------------------------------
-- 4. TABLA: CUOTA
-- Obligación mensual generada para cada jugador habilitado (no dado de baja).
-- -----------------------------------------------------------------------------
CREATE TABLE CUOTA (
    id_cuota          INT           AUTO_INCREMENT PRIMARY KEY,
    mes               TINYINT       NOT NULL,
    anio              SMALLINT      NOT NULL,
    monto             DECIMAL(10,2) NOT NULL,
    fecha_vencimiento DATE          NOT NULL,
    estado_pago       VARCHAR(10)   NOT NULL DEFAULT 'En mora',
    dni_jugador       VARCHAR(20)   NOT NULL,
    CONSTRAINT uq_cuota_periodo   UNIQUE (dni_jugador, mes, anio),   -- una por jugador y mes
    CONSTRAINT ck_cuota_mes       CHECK (mes BETWEEN 1 AND 12),
    CONSTRAINT ck_cuota_anio      CHECK (anio BETWEEN 2020 AND 2100),
    CONSTRAINT ck_cuota_monto     CHECK (monto > 0),
    CONSTRAINT ck_cuota_estado    CHECK (estado_pago IN ('En mora', 'Al día')),
    CONSTRAINT fk_cuota_jugador FOREIGN KEY (dni_jugador)
        REFERENCES JUGADOR(dni)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- -----------------------------------------------------------------------------
-- 5. TABLA: PAGO
-- Transacción que salda una cuota específica, validada por un administrador.
-- -----------------------------------------------------------------------------
CREATE TABLE PAGO (
    id_pago          INT           AUTO_INCREMENT PRIMARY KEY,
    fecha            DATE          NOT NULL,
    monto            DECIMAL(10,2) NOT NULL,
    medio_pago       VARCHAR(20)   NOT NULL,
    comprobante      VARCHAR(255)  NULL,
    id_cuota         INT           NOT NULL,
    id_administrador INT           NOT NULL,
    CONSTRAINT uq_pago_cuota  UNIQUE (id_cuota),                    -- "Aplica a" 1 a 1
    CONSTRAINT ck_pago_monto  CHECK (monto > 0),
    CONSTRAINT ck_pago_medio  CHECK (medio_pago IN ('Efectivo', 'Transferencia', 'Tarjeta')),
    CONSTRAINT fk_pago_cuota FOREIGN KEY (id_cuota)
        REFERENCES CUOTA(id_cuota)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_pago_administrador FOREIGN KEY (id_administrador)
        REFERENCES ADMINISTRADOR(id_administrador)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Índices de apoyo para las consultas más frecuentes de la interfaz
CREATE INDEX ix_cuota_estado ON CUOTA (estado_pago, anio, mes);
CREATE INDEX ix_pago_fecha   ON PAGO (fecha);

-- =============================================================================
-- REGLAS DE INTEGRIDAD PROCEDURALES (TRIGGERS)
-- =============================================================================
DELIMITER $$

-- Regla 2: solo se generan cuotas para jugadores habilitados (no dados de baja).
CREATE TRIGGER trg_cuota_bi_jugador_habilitado
BEFORE INSERT ON CUOTA
FOR EACH ROW
BEGIN
    IF (SELECT estado_deportivo FROM JUGADOR WHERE dni = NEW.dni_jugador) = 'Baja' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se puede generar una cuota para un jugador dado de baja.';
    END IF;
END$$

-- Regla 4: el pago debe cubrir el importe de la cuota y la cuota no puede estar saldada.
CREATE TRIGGER trg_pago_bi_validar
BEFORE INSERT ON PAGO
FOR EACH ROW
BEGIN
    DECLARE v_monto_cuota DECIMAL(10,2);
    DECLARE v_estado      VARCHAR(10);

    SELECT monto, estado_pago INTO v_monto_cuota, v_estado
    FROM CUOTA WHERE id_cuota = NEW.id_cuota;

    IF v_estado = 'Al día' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La cuota ya se encuentra saldada.';
    END IF;
    IF NEW.monto < v_monto_cuota THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El monto abonado es menor al importe de la cuota.';
    END IF;
END$$

-- Regla 3: al registrarse el pago, la cuota pasa de 'En mora' a 'Al día'.
CREATE TRIGGER trg_pago_ai_saldar_cuota
AFTER INSERT ON PAGO
FOR EACH ROW
BEGIN
    UPDATE CUOTA SET estado_pago = 'Al día' WHERE id_cuota = NEW.id_cuota;
END$$

DELIMITER ;

-- =============================================================================
-- VISTAS DE CONSULTA (las usa la interfaz y el rol de solo lectura)
-- =============================================================================

-- Padrón general: una fila por jugador con su responsable y su condición de pago.
CREATE VIEW v_padron_jugadores AS
SELECT  j.dni,
        CONCAT(j.nombre, ' ', j.apellido)              AS nombre_completo,
        j.correo_electronico,
        j.fecha_nacimiento,
        c.nombre_categoria                             AS categoria,
        IF(j.es_federado, 'Sí', 'No')                  AS federado,
        j.estado_deportivo,
        a.nombre                                       AS responsable,
        IF(EXISTS (SELECT 1 FROM CUOTA cu
                   WHERE cu.dni_jugador = j.dni AND cu.estado_pago = 'En mora'),
           'En mora', 'Al día')                        AS estado_cuenta
FROM JUGADOR j
JOIN CATEGORIA c     ON c.id_categoria     = j.id_categoria
JOIN ADMINISTRADOR a ON a.id_administrador = j.id_administrador;

-- Deudores: jugadores con cuotas impagas, cantidad de meses y deuda acumulada.
CREATE VIEW v_deudores AS
SELECT  j.dni,
        CONCAT(j.nombre, ' ', j.apellido)                              AS nombre_completo,
        c.nombre_categoria                                             AS categoria,
        COUNT(cu.id_cuota)                                             AS meses_adeudados,
        GROUP_CONCAT(CONCAT(LPAD(cu.mes, 2, '0'), '/', cu.anio)
                     ORDER BY cu.anio, cu.mes SEPARATOR ', ')          AS periodos,
        SUM(cu.monto)                                                  AS deuda_total
FROM JUGADOR j
JOIN CATEGORIA c ON c.id_categoria = j.id_categoria
JOIN CUOTA cu    ON cu.dni_jugador = j.dni AND cu.estado_pago = 'En mora'
GROUP BY j.dni, j.nombre, j.apellido, c.nombre_categoria;

-- Historial unificado de pagos recibidos.
CREATE VIEW v_historial_pagos AS
SELECT  p.id_pago,
        p.fecha,
        j.dni,
        CONCAT(j.nombre, ' ', j.apellido)                  AS nombre_completo,
        CONCAT(LPAD(cu.mes, 2, '0'), '/', cu.anio)         AS periodo,
        cu.mes,
        cu.anio,
        p.monto,
        p.medio_pago,
        p.comprobante,
        a.nombre                                           AS validado_por
FROM PAGO p
JOIN CUOTA cu        ON cu.id_cuota        = p.id_cuota
JOIN JUGADOR j       ON j.dni              = cu.dni_jugador
JOIN ADMINISTRADOR a ON a.id_administrador = p.id_administrador;