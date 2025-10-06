"""
Migration script: Ensure movement tables have proper column types.
- existencia_inicial: cantidad INT, costo DECIMAL(10,2)
- entradas: cantidad INT, costo DECIMAL(10,2)
- salidas: cantidad INT, costo DECIMAL(10,2)
- existencia_final: cantidad INT, costo DECIMAL(10,2)

Safe operations:
- Creates missing columns with default values (0 / 0.00).
- Alters column types if they exist with a different type.

Run:
  /Users/dmrodriguez/TDR/entorno/bin/python db/migrations/ensure_movimientos_types.py
"""
from __future__ import annotations

import os
import sys
import logging
from typing import Optional

# Ensure project root in sys.path so we can import db and config
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_utils import ConnectionManager, DatabaseError  # type: ignore
from config import db_config  # type: ignore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

TABLES = [
    "existencia_inicial",
    "entradas",
    "salidas",
    "existencia_final",
]

CANTIDAD_DEF = "INT"
COSTO_DEF = "DECIMAL(10,2)"


def get_db_name() -> str:
    # Try to infer db name from config
    try:
        return db_config.DB_NAME  # type: ignore[attr-defined]
    except Exception:
        # Fallback: ask the server
        with ConnectionManager.get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT DATABASE() AS db")
                row = cur.fetchone() or {}
                return row.get("db") or ""


def column_info(cursor, table: str, column: str, db_name: str) -> Optional[dict]:
    cursor.execute(
        """
        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (db_name, table, column),
    )
    return cursor.fetchone()


def ensure_column(cursor, table: str, column: str, target_type: str) -> None:
    db_name = get_db_name()
    info = column_info(cursor, table, column, db_name)
    if info is None:
        # Add missing column with NOT NULL and sensible default
        default_clause = "DEFAULT 0.00" if target_type.startswith("DECIMAL") else "DEFAULT 0"
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {target_type} NOT NULL {default_clause}"
        logger.info("Adding missing column %s.%s %s", table, column, target_type)
        cursor.execute(sql)
        return

    # Normalize types for comparison (case-insensitive)
    current = (info.get("COLUMN_TYPE") or "").upper()
    target = target_type.upper()
    if current != target:
        # Modify type preserving NOT NULL, set default 0/0.00 to be safe
        default_clause = "DEFAULT 0.00" if target_type.startswith("DECIMAL") else "DEFAULT 0"
        sql = f"ALTER TABLE {table} MODIFY COLUMN {column} {target_type} NOT NULL {default_clause}"
        logger.info("Altering column %s.%s from %s to %s", table, column, current, target)
        cursor.execute(sql)


def main() -> None:
    logger.info("Ensuring movement tables have cantidad INT and costo DECIMAL(10,2)...")
    try:
        with ConnectionManager.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                for table in TABLES:
                    ensure_column(cursor, table, "cantidad", CANTIDAD_DEF)
                    ensure_column(cursor, table, "costo", COSTO_DEF)
            conn.commit()
        logger.info("Migration completed successfully.")
    except DatabaseError as e:
        logger.exception("Database error: %s", e)
        raise
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise


if __name__ == "__main__":
    main()
