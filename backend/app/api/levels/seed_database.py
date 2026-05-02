"""Apply in-memory SQLite schema + rows for a given main level from `LEVEL_CONFIGS`."""

from __future__ import annotations

import re
import sqlite3

from app.api.levels.levelsdata import LEVEL_CONFIGS

_TABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def seed_level(conn: sqlite3.Connection, level: int) -> None:
    """
    Run the level's DDL then INSERT all configured tables.
    Table names must match `[A-Za-z_][A-Za-z0-9_]*` (defense in depth; values come from code only).
    """
    cfg = LEVEL_CONFIGS.get(level)
    if cfg is None:
        raise ValueError(f"No LEVEL_CONFIGS entry for level={level}")

    conn.executescript(cfg["ddl"])

    for table, rows in cfg["tables"].items():
        if not _TABLE_NAME.fullmatch(table):
            raise ValueError(f"Invalid table name for seed: {table!r}")
        if not rows:
            continue
        keys = list(rows[0].keys())
        cols = ", ".join(keys)
        placeholders = ", ".join(f":{k}" for k in keys)
        conn.executemany(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
            rows,
        )

    conn.commit()
