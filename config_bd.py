import os

DB_CONFIG = {
    "host": os.getenv("GPJ_DB_HOST", "localhost"),
    "port": int(os.getenv("GPJ_DB_PORT", "3306")),
    "user": os.getenv("GPJ_DB_USER", "app_gpj"),
    "password": os.getenv("GPJ_DB_PASSWORD", "AppGPJ#2026"),
    "database": os.getenv("GPJ_DB_NAME", "bd_club_deportivo"),
}