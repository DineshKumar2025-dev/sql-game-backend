import sqlite3

from app.api.levels.levelsdata import LEVEL1_DATA, LEVEL1_STATIC_QUERIES


def _seed_database(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            role TEXT,
            salary INTEGER,
            status TEXT,
            joined_date TEXT,
            floor INTEGER,
            clearance TEXT
        );

        CREATE TABLE access_logs (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            location TEXT,
            timestamp TEXT,
            action TEXT
        );
        """
    )
    conn.executemany(
        """
        INSERT INTO employees (id, name, department, role, salary, status, joined_date, floor, clearance)
        VALUES (:id, :name, :department, :role, :salary, :status, :joined_date, :floor, :clearance)
        """,
        LEVEL1_DATA["employees"],
    )
    conn.executemany(
        """
        INSERT INTO access_logs (id, employee_id, location, timestamp, action)
        VALUES (:id, :employee_id, :location, :timestamp, :action)
        """,
        LEVEL1_DATA["access_logs"],
    )
    conn.commit()


def _rows_to_set(rows: list[dict[str, object]]) -> set[tuple[tuple[str, object], ...]]:
    normalized: set[tuple[tuple[str, object], ...]] = set()
    for row in rows:
        normalized.add(tuple(sorted(row.items())))
    return normalized


def verify_sublevel(query: str, sublevel: int) -> dict[str, object]:
    expected_query = LEVEL1_STATIC_QUERIES.get(sublevel)
    if expected_query is None:
        return {
            "is_correct": False,
            "error": f"No static query configured for sublevel {sublevel}.",
            "output": [],
            "level1_output": [],
        }

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    try:
        _seed_database(conn)

        player_cursor = conn.execute(query)
        output = [dict(row) for row in player_cursor.fetchall()]

        expected_cursor = conn.execute(expected_query)
        level1_output = [dict(row) for row in expected_cursor.fetchall()]
    except sqlite3.Error as exc:
        return {
            "is_correct": False,
            "error": str(exc),
            "output": [],
            "level1_output": [],
        }
    finally:
        conn.close()

    is_correct = _rows_to_set(output) == _rows_to_set(level1_output)
    return {
        "is_correct": is_correct,
        "error": None,
        "output": output,
        "level1_output": level1_output,
    }
