-- =============================================================================
-- DATOS DE PRUEBA - bd_club_deportivo
-- Grupo: Inteligencia Disfuncional - ISPC Módulo Programador 2026
-- Ejecutar después del DDL v5. Las contraseñas se guardan con SHA2(...,256).
--   Administradores: tesoreria@generalpazjunior.com / admin123
--                    secretaria@generalpazjunior.com / admin123
--   Socios: usuario = DNI, contraseña = socio123
-- =============================================================================
-- Asegura que los acentos (día, Gómez) se guarden bien en cualquier cliente
SET NAMES utf8mb4;

USE bd_club_deportivo;

-- -----------------------------------------------------------------------------
-- CATEGORÍAS (regla de negocio 6) con el importe mensual de cada una
-- -----------------------------------------------------------------------------
INSERT INTO CATEGORIA (nombre_categoria, monto_cuota) VALUES
    ('Mini''s',              3500.00),
    ('Infantil Femenino',    4500.00),
    ('Infantil Masculino',   4500.00),
    ('Menor Femenino',       4500.00),
    ('Menor Masculino',      4500.00),
    ('Cadete Femenino',      5000.00),
    ('Cadete Masculino',     5000.00),
    ('Juvenil Femenino',     5000.00),
    ('Juvenil Masculino',    5000.00),
    ('Primera Femenina',     5500.00),
    ('Primera Masculina',    5500.00);

-- -----------------------------------------------------------------------------
-- ADMINISTRADORES
-- -----------------------------------------------------------------------------
INSERT INTO ADMINISTRADOR (nombre, correo, contrasena) VALUES
    ('Tesorero Principal',   'tesoreria@generalpazjunior.com',  SHA2('admin123', 256)),
    ('Secretaría Deportiva', 'secretaria@generalpazjunior.com', SHA2('admin123', 256));

-- -----------------------------------------------------------------------------
-- JUGADORES (uno o más por categoría, con distintos estados y condición federativa)
-- -----------------------------------------------------------------------------
INSERT INTO JUGADOR (dni, nombre, apellido, fecha_nacimiento, correo_electronico, contrasena,
                     es_federado, estado_deportivo, id_categoria, id_administrador)
SELECT d.dni, d.nombre, d.apellido, d.fnac, d.correo, SHA2('socio123', 256),
       d.fed, d.estado, c.id_categoria, d.adm
FROM (
    SELECT '58123456' AS dni, 'Tomás' AS nombre, 'Ledesma' AS apellido, DATE('2019-05-14') AS fnac,
           'tomas.ledesma@mail.com' AS correo, FALSE AS fed, 'Activo' AS estado, 'Mini''s' AS cat, 2 AS adm
    UNION ALL SELECT '54876543','Valentina','Sosa','2014-08-02','valentina.sosa@mail.com',TRUE,'Activo','Infantil Femenino',2
    UNION ALL SELECT '55234567','Benjamín','Ríos','2015-03-21','benjamin.rios@mail.com',FALSE,'Activo','Infantil Masculino',2
    UNION ALL SELECT '52345678','Martina','Quiroga','2012-11-09','martina.quiroga@mail.com',TRUE,'Lesionado','Menor Femenino',2
    UNION ALL SELECT '53456789','Lucas','Gómez','2013-01-30','lucas.gomez@mail.com',FALSE,'Activo','Menor Masculino',1
    UNION ALL SELECT '51234567','Camila','Bustos','2011-06-17','camila.bustos@mail.com',TRUE,'Activo','Cadete Femenino',2
    UNION ALL SELECT '50987654','Carlos','Rodríguez','2010-09-05','carlos.rod@mail.com',TRUE,'Activo','Cadete Masculino',1
    UNION ALL SELECT '49123456','Sofía','Moyano','2009-04-12','sofia.moyano@mail.com',TRUE,'Activo','Juvenil Femenino',2
    UNION ALL SELECT '48765432','Mateo','Ferreyra','2008-12-01','mateo.ferreyra@mail.com',FALSE,'Baja','Juvenil Masculino',1
    UNION ALL SELECT '44556677','Andrea','Fernández','2002-07-23','andrea.f@mail.com',FALSE,'Activo','Primera Femenina',1
    UNION ALL SELECT '35123456','Carlos','Gaetán','1990-10-03','carlos.gaetan@generalpazjunior.com',TRUE,'Activo','Primera Masculina',1
    UNION ALL SELECT '38765432','Juan','Pérez','1995-02-14','juan.perez@mail.com',TRUE,'Activo','Primera Masculina',1
) AS d
JOIN CATEGORIA c ON c.nombre_categoria = d.cat;

-- -----------------------------------------------------------------------------
-- CUOTAS: agosto, septiembre y octubre de 2026 (vencen el día 10).
-- Es la misma sentencia que usa la aplicación para "Generar cuotas del mes":
-- solo jugadores habilitados y sin duplicar períodos.
-- -----------------------------------------------------------------------------
INSERT INTO CUOTA (mes, anio, monto, fecha_vencimiento, dni_jugador)
SELECT p.mes, 2026, c.monto_cuota, DATE(CONCAT('2026-', p.mes, '-10')), j.dni
FROM JUGADOR j
JOIN CATEGORIA c ON c.id_categoria = j.id_categoria
CROSS JOIN (SELECT 8 AS mes UNION ALL SELECT 9 UNION ALL SELECT 10) AS p
WHERE j.estado_deportivo <> 'Baja'
  AND NOT EXISTS (SELECT 1 FROM CUOTA x
                  WHERE x.dni_jugador = j.dni AND x.mes = p.mes AND x.anio = 2026);

-- -----------------------------------------------------------------------------
-- PAGOS
-- Primero se arma la lista en una tabla temporal: MySQL no permite que el trigger
-- trg_pago_ai_saldar_cuota modifique CUOTA si la misma sentencia está leyendo CUOTA.
-- Al insertar cada pago, el trigger pasa la cuota a 'Al día'.
-- -----------------------------------------------------------------------------
CREATE TEMPORARY TABLE tmp_pagos AS
-- Agosto: pagan todos menos Lucas Gómez
SELECT DATE('2026-08-07') AS fecha, cu.monto,
       IF(j.es_federado, 'Transferencia', 'Efectivo') AS medio_pago,
       IF(j.es_federado, CONCAT('comprobante_ago_', cu.dni_jugador, '.png'), NULL) AS comprobante,
       cu.id_cuota, 1 AS id_administrador
FROM CUOTA cu JOIN JUGADOR j ON j.dni = cu.dni_jugador
WHERE cu.mes = 8 AND cu.anio = 2026 AND cu.dni_jugador <> '53456789'
UNION ALL
-- Septiembre: no pagan Lucas Gómez ni Carlos Rodríguez
SELECT '2026-09-09', cu.monto, 'Transferencia',
       CONCAT('comprobante_sep_', cu.dni_jugador, '.png'), cu.id_cuota, 1
FROM CUOTA cu
WHERE cu.mes = 9 AND cu.anio = 2026 AND cu.dni_jugador NOT IN ('53456789', '50987654')
UNION ALL
-- Octubre: pagan solo seis jugadores
SELECT '2026-10-08', cu.monto, 'Tarjeta', NULL, cu.id_cuota, 2
FROM CUOTA cu
WHERE cu.mes = 10 AND cu.anio = 2026
  AND cu.dni_jugador IN ('35123456', '38765432', '44556677', '54876543', '51234567', '49123456');

INSERT INTO PAGO (fecha, monto, medio_pago, comprobante, id_cuota, id_administrador)
SELECT fecha, monto, medio_pago, comprobante, id_cuota, id_administrador
FROM tmp_pagos
ORDER BY fecha, id_cuota;

DROP TEMPORARY TABLE tmp_pagos;

-- Los INSERT ... SELECT reservan valores de AUTO_INCREMENT por bloques; esto devuelve
-- cada contador al siguiente número libre para que los próximos IDs sean consecutivos.
ALTER TABLE CUOTA AUTO_INCREMENT = 1;
ALTER TABLE PAGO  AUTO_INCREMENT = 1;