-- IMPORTANTE: las contraseñas de abajo son solo para el entorno de prueba.
-- =============================================================================

-- Asegura que los acentos (día, Gómez) se guarden bien en cualquier cliente
SET NAMES utf8mb4;

-- Limpieza para poder re-ejecutar el script
DROP USER IF EXISTS 'dba_gpj'@'localhost', 'app_gpj'@'localhost', 'consulta_gpj'@'localhost';
DROP ROLE IF EXISTS 'rol_dba_club', 'rol_app_club', 'rol_lectura_club';
