import sqlite3

from app.api.levels.levelsdata import LEVEL_CONFIGS
from app.api.levels.seed_database import seed_level


def _rows_to_set(rows: list[dict[str, object]]) -> set[tuple[tuple[str, object], ...]]:
    normalized: set[tuple[tuple[str, object], ...]] = set()
    for row in rows:
        normalized.add(tuple(sorted(row.items())))
    return normalized


def verify_sublevel(query: str, level: int, sublevel: str) -> dict[str, object]:
    """
    Run player query vs canonical `static_queries[sublevel]` on the same seeded DB.
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

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    try:
        seed_level(conn, level)

        player_cursor = conn.execute(query)
        output = [dict(row) for row in player_cursor.fetchall()]

        expected_cursor = conn.execute(expected_query)
        level_output = [dict(row) for row in expected_cursor.fetchall()]
    except sqlite3.Error as exc:
        return {
            "is_correct": False,
            "error": str(exc),
            "output": [],
            "level_output": [],
        }
    finally:
        conn.close()

    is_correct = _rows_to_set(output) == _rows_to_set(level_output)
    return {
        "is_correct": is_correct,
        "error": None,
        "output": output,
        "level_output": level_output,
    }
