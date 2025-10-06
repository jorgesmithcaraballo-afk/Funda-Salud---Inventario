"""
Migration: Move business key from id to codigo and re-sequence id as AUTO_INCREMENT

- Reads existing Inventario rows.
- Ensures 'codigo' exists and is populated from current 'id'.
- Creates a tmp table, inserts rows (letting MySQL assign new ids).
- Builds a mapping old_id -> new_id using 'codigo'.
- Updates child tables' FKs to point to new ids.
- Swaps tmp with original Inventario.

Run with the project virtualenv python:
/Users/dmrodriguez/TDR/entorno/bin/python db/migrations/migrate_codigo_from_id.py
"""
from __future__ import annotations

import logging
from typing import Optional

import os
import sys

# Ensure project root is on sys.path so 'db' and 'config' packages can be imported
# This allows running the script directly: python db/migrations/migrate_codigo_from_id.py
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_utils import ConnectionManager, DatabaseError
from config import db_config

logger = logging.getLogger("db.migrations.migrate_codigo_from_id")
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def table_exists(cursor, table_name: str, db_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) as count
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        """,
        (db_name, table_name),
    )
    row = cursor.fetchone()
    return bool(row and row.get("count", 0) > 0)


def index_exists(cursor, table_name: str, index_name: str, db_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) as count
        FROM information_schema.statistics
        WHERE table_schema = %s AND table_name = %s AND index_name = %s
        """,
        (db_name, table_name, index_name),
    )
    row = cursor.fetchone()
    return bool(row and row.get("count", 0) > 0)


def column_exists(cursor, table_name: str, column_name: str, db_name: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) as count
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s AND column_name = %s
        """,
        (db_name, table_name, column_name),
    )
    row = cursor.fetchone()
    return bool(row and row.get("count", 0) > 0)


def run_migration() -> None:
    mysql_conf = db_config.get_mysql_config()
    db_name = mysql_conf["database"]

    with ConnectionManager.get_connection(mysql_conf) as conn:
        with ConnectionManager.get_cursor(conn) as cursor:
            logger.info("Starting migration to introduce 'codigo' as business key and resequence 'id'.")

            # Disable FK checks
            cursor.execute("SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            try:
                # Ensure Inventario table exists
                if not table_exists(cursor, "Inventario", db_name):
                    raise DatabaseError("Inventario table does not exist. Aborting migration.")

                # 1) Add 'codigo' column if missing (NULLable for backfill)
                if not column_exists(cursor, "Inventario", "codigo", db_name):
                    logger.info("Adding column 'codigo' to Inventario (NULLable for backfill)...")
                    cursor.execute("ALTER TABLE Inventario ADD COLUMN codigo VARCHAR(50) NULL;")

                # 2) Backfill 'codigo' from existing 'id' when needed
                logger.info("Backfilling 'codigo' from 'id' for existing rows...")
                cursor.execute(
                    "UPDATE Inventario SET codigo = CAST(id AS CHAR) WHERE codigo IS NULL OR codigo = '';"
                )

                # 3) Create tmp table and ensure constraints
                logger.info("Creating temporary table Inventario_tmp with target schema...")
                cursor.execute("DROP TABLE IF EXISTS Inventario_tmp;")
                cursor.execute("CREATE TABLE Inventario_tmp LIKE Inventario;")

                # Ensure constraints on tmp
                # Do NOT redefine PRIMARY KEY; table created LIKE retains it. Only set AUTO_INCREMENT attribute.
                cursor.execute(
                    "ALTER TABLE Inventario_tmp MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT;"
                )
                cursor.execute(
                    "ALTER TABLE Inventario_tmp MODIFY COLUMN codigo VARCHAR(50) NOT NULL;"
                )
                # Add unique index for codigo if not already present on tmp
                if not index_exists(cursor, "Inventario_tmp", "uq_inventario_codigo", db_name):
                    cursor.execute(
                        "ALTER TABLE Inventario_tmp ADD UNIQUE KEY uq_inventario_codigo (codigo);"
                    )

                # 4) Insert rows into tmp letting MySQL assign new 'id'
                logger.info("Copying rows into Inventario_tmp (new ids will be assigned)...")
                cursor.execute(
                    """
                    INSERT INTO Inventario_tmp (codigo, descripcion_insumo, tipo, cantidad, costo_unitario, monto_total, categoria)
                    SELECT codigo, descripcion_insumo, tipo, cantidad, costo_unitario, monto_total, categoria
                    FROM Inventario;
                    """
                )

                # 5) Build mapping old_id -> new_id using 'codigo'
                logger.info("Creating id mapping (old_id -> new_id) via 'codigo'...")
                cursor.execute("DROP TEMPORARY TABLE IF EXISTS Inventario_id_map;")
                cursor.execute(
                    """
                    CREATE TEMPORARY TABLE Inventario_id_map (
                        old_id INT NOT NULL,
                        new_id INT NOT NULL,
                        codigo VARCHAR(50) NOT NULL,
                        PRIMARY KEY (old_id),
                        UNIQUE KEY uq_codigo (codigo)
                    );
                    """
                )
                cursor.execute(
                    """
                    INSERT INTO Inventario_id_map (old_id, new_id, codigo)
                    SELECT old_i.id AS old_id, new_i.id AS new_id, new_i.codigo
                    FROM Inventario AS old_i
                    JOIN Inventario_tmp AS new_i ON new_i.codigo = old_i.codigo;
                    """
                )

                # 6) Update child tables if they exist
                for child in ("existencia_inicial", "entradas", "salidas", "existencia_final"):
                    if table_exists(cursor, child, db_name):
                        logger.info(f"Updating FK references in {child}...")
                        cursor.execute(
                            f"""
                            UPDATE {child} c
                            JOIN Inventario_id_map m ON m.old_id = c.inventario_id
                            SET c.inventario_id = m.new_id;
                            """
                        )
                    else:
                        logger.info(f"Table {child} does not exist, skipping FK update.")

                # 7) Swap tables
                logger.info("Swapping Inventario tables (drop original, rename tmp)...")
                cursor.execute("DROP TABLE Inventario;")
                cursor.execute("RENAME TABLE Inventario_tmp TO Inventario;")

                # 8) Re-enable FK checks
                cursor.execute("SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;")

                conn.commit()
                logger.info("Migration completed successfully.")

            except Exception as e:
                conn.rollback()
                # Re-enable FK checks on rollback as well
                try:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;")
                except Exception:
                    pass
                logger.error(f"Migration failed and was rolled back: {e}")
                raise


if __name__ == "__main__":
    run_migration()
