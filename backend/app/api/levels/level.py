import sqlite3
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from app.api.routes.auth import _database_url
from app.api.levels.levelsdata import LEVEL_CONFIGS
from app.api.levels.seed_database import seed_level


def _rows_to_set(rows: list[dict[str, object]]) -> set[tuple[tuple[str, object], ...]]:
    normalized: set[tuple[tuple[str, object], ...]] = set()
    for row in rows:
        normalized.add(tuple(sorted(row.items())))
    return normalized


def is_final_sublevel(level: int, sublevel: str) -> bool:
    """True if `sublevel` is the last key in that level's `static_queries` (insertion order)."""
    cfg = LEVEL_CONFIGS.get(level)
    if cfg is None:
        return False
    keys = list(cfg["static_queries"].keys())
    return bool(keys) and keys[-1] == sublevel


def verify_sublevel(query: str, level: int, sublevel: str) -> dict[str, object]:
    """
    Run player SQL vs canonical `static_queries[sublevel]` on seeded in-memory SQLite.

    For read-only levels the player SQL is typically a single SELECT; for write-heavy levels
    (CRUD/transactions/indexing) the player SQL may be a multi-statement script.

    In those cases, we execute the player's script, then evaluate correctness by running a
    deterministic `check_queries[sublevel]` SELECT (if configured) on both the player's DB state
    and the expected DB state.
    Sublevel ids match the client (e.g. level 1 → l11, l12, …).
    Add levels only in `levelsdata.LEVEL_CONFIGS` (+ `seed_level` uses them automatically).
    """
    cfg = LEVEL_CONFIGS.get(level)
    if cfg is None:
        return {
            "is_correct": False,
            "error": f"No level configuration for level {level}.",
            "output": [],
            "level_output": [],
        }

    expected_query = cfg["static_queries"].get(sublevel)
    if expected_query is None:
        return {
            "is_correct": False,
            "error": f"No static query configured for level {level}, sublevel {sublevel}.",
            "output": [],
            "level_output": [],
        }

    check_query = cfg.get("check_queries", {}).get(sublevel) if isinstance(cfg, dict) else None
    if not check_query:
        check_query = expected_query

    def _run_script(conn: sqlite3.Connection, sql: str) -> None:
        # executescript supports multi-statement SQL; it does not return rows.
        conn.executescript(sql)

    def _run_select(conn: sqlite3.Connection, sql: str) -> list[dict[str, object]]:
        cur = conn.execute(sql)
        return [dict(row) for row in cur.fetchall()]

    player_conn = sqlite3.connect(":memory:")
    player_conn.row_factory = sqlite3.Row
    expected_conn = sqlite3.connect(":memory:")
    expected_conn.row_factory = sqlite3.Row

    try:
        seed_level(player_conn, level)
        seed_level(expected_conn, level)

        # Apply player SQL (may mutate DB).
        _run_script(player_conn, query)

        # Apply expected SQL (may mutate DB).
        _run_script(expected_conn, expected_query)

        # Compare deterministic check query results after the scripts.
        output = _run_select(player_conn, check_query)
        level_output = _run_select(expected_conn, check_query)
    except sqlite3.Error as exc:
        return {
            "is_correct": False,
            "error": str(exc),
            "output": [],
            "level_output": [],
        }
    finally:
        player_conn.close()
        expected_conn.close()

    is_correct = _rows_to_set(output) == _rows_to_set(level_output)
    return {
        "is_correct": is_correct,
        "error": None,
        "output": output,
        "level_output": level_output,
    }


logger = logging.getLogger(__name__)

def level_sublevel(level: int, user_id: int) -> dict[str, object] | None:
    conn = psycopg2.connect(_database_url())
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT "
                "    MAX(l.id) AS highest_level_completed, "
                "    lc.status "
                "FROM levelscompleted lc "
                "JOIN levels l "
                "    ON lc.level_id = l.id "
                "    AND l.main_level = %s "
                "WHERE lc.user_id = %s "
                "GROUP BY lc.status",
                (level, user_id),
            )
            row = cursor.fetchone()   # ← fetchone(), not fetchall()

            if row is None:
                return None

            return {
                "level_id": row["highest_level_completed"],
                "status":   row["status"],
            }

    except psycopg2.Error as e:
        logger.error("Database error in level_sublevel: %s", e)
        raise
    finally:
        conn.close()

def sublevel_query(level_key: str, user_id: int) -> str | None:
    """level_key matches verifycode storage (e.g. l11), not numeric levels.id."""
    conn = psycopg2.connect(_database_url())
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT query FROM levelscompleted WHERE level_id = %s AND user_id = %s",
                (level_key, user_id),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            q = row["query"]
            return None if q is None else str(q)
    except psycopg2.Error as e:
        logger.error("Database error in sublevel_query: %s", e)
        raise
    finally:
        conn.close()