-- IMPORTANTE: las contraseñas de abajo son solo para el entorno de prueba.
-- =============================================================================

-- Asegura que los acentos (día, Gómez) se guarden bien en cualquier cliente
SET NAMES utf8mb4;

-- Limpieza para poder re-ejecutar el script
DROP USER IF EXISTS 'dba_gpj'@'localhost', 'app_gpj'@'localhost', 'consulta_gpj'@'localhost';
DROP ROLE IF EXISTS 'rol_dba_club', 'rol_app_club', 'rol_lectura_club';



------------------------------------- ROLES -------------------------------------

CREATE ROLE 'rol_dba_club',      -- mantenimiento completo del esquema
            'rol_app_club',      -- la aplicación Tkinter (operaciones del día a día)
            'rol_lectura_club';  -- auditoría / reportes: solo consulta de vistas

-- rol_dba_club: control total sobre la base del club
GRANT ALL PRIVILEGES ON bd_club_deportivo.* TO 'rol_dba_club';

-- rol_app_club: consulta todo, da de alta y modifica, pero NO borra
GRANT SELECT                 ON bd_club_deportivo.*             TO 'rol_app_club';
GRANT INSERT, UPDATE         ON bd_club_deportivo.JUGADOR       TO 'rol_app_club';
GRANT INSERT, UPDATE         ON bd_club_deportivo.CUOTA         TO 'rol_app_club';
GRANT INSERT, UPDATE         ON bd_club_deportivo.CATEGORIA     TO 'rol_app_club';
GRANT INSERT                 ON bd_club_deportivo.PAGO          TO 'rol_app_club';
-- (ADMINISTRADOR queda en solo lectura para la app: solo se usa para el login)

-- rol_lectura_club: únicamente las vistas (no ve contraseñas ni tablas base)
GRANT SELECT ON bd_club_deportivo.v_padron_jugadores TO 'rol_lectura_club';
GRANT SELECT ON bd_club_deportivo.v_deudores         TO 'rol_lectura_club';
GRANT SELECT ON bd_club_deportivo.v_historial_pagos  TO 'rol_lectura_club';



---------------------------- USUARIOS Y ASIGNACIÓN DE ROLES ------------------------------

CREATE USER 'dba_gpj'@'localhost'      IDENTIFIED BY 'DbaGPJ#2026';
CREATE USER 'app_gpj'@'localhost'      IDENTIFIED BY 'AppGPJ#2026';
CREATE USER 'consulta_gpj'@'localhost' IDENTIFIED BY 'ConsultaGPJ#2026';

GRANT 'rol_dba_club'     TO 'dba_gpj'@'localhost';
GRANT 'rol_app_club'     TO 'app_gpj'@'localhost';
GRANT 'rol_lectura_club' TO 'consulta_gpj'@'localhost';

-- Los roles quedan activos automáticamente al iniciar sesión
SET DEFAULT ROLE ALL TO 'dba_gpj'@'localhost', 'app_gpj'@'localhost', 'consulta_gpj'@'localhost';



--------------------------------------- VERIFICACIÓN -----------------------------------

SHOW GRANTS FOR 'app_gpj'@'localhost' USING 'rol_app_club';
SHOW GRANTS FOR 'consulta_gpj'@'localhost' USING 'rol_lectura_club';