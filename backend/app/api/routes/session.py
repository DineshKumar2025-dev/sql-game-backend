import sqlite3
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel


router = APIRouter()


class QueryRequest(BaseModel):
    sql: str


class ValidateRequest(BaseModel):
    sql: str
    level_id: str


class SessionStore:
    def __init__(self) -> None:
        self._connections: dict[str, sqlite3.Connection] = {}
        self._lock = Lock()

    def create_session(self) -> str:
        session_id = str(uuid4())
        connection = sqlite3.connect(":memory:", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        with self._lock:
            self._connections[session_id] = connection
        return session_id

    def get_connection(self, session_id: str) -> sqlite3.Connection:
        with self._lock:
            connection = self._connections.get(session_id)
        if connection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unknown session: {session_id}",
            )
        return connection


session_store = SessionStore()


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        DROP TABLE IF EXISTS access_logs;
        DROP TABLE IF EXISTS employees;

        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            salary INTEGER NOT NULL,
            status TEXT NOT NULL,
            joined_date TEXT NOT NULL,
            floor INTEGER NOT NULL,
            clearance TEXT NOT NULL
        );

        CREATE TABLE access_logs (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER NOT NULL,
            location TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        );
        """
    )

    employees = [
        (1, "Dr. Riya Sharma", "Engineering", "Lead Scientist", 210000, "missing", "2040-02-18", 3, "CLASSIFIED"),
        (2, "Marcus Holt", "Security", "Security Chief", 130000, "active", "2038-06-01", 1, "CLASSIFIED"),
        (3, "Petra Novak", "Security", "Security Analyst", 98000, "active", "2042-03-11", 1, "HIGH"),
        (4, "Nadia Kim", "Engineering", "Data Engineer", 125000, "active", "2043-11-19", 2, "HIGH"),
        (5, "Leo Grant", "Operations", "Facility Manager", 90000, "active", "2041-08-07", 1, "MEDIUM"),
        (6, "Ethan Cross", "Engineering", "Systems Engineer", 118000, "suspended", "2041-01-15", 3, "HIGH"),
        (7, "Ava Patel", "Research", "Analyst", 101000, "active", "2044-05-27", 4, "HIGH"),
        (8, "Noah Silva", "IT", "Network Engineer", 99000, "active", "2040-09-14", 2, "MEDIUM"),
        (9, "Priya Das", "Security", "Shift Supervisor", 110000, "active", "2039-12-30", 1, "HIGH"),
    ]
    connection.executemany(
        """
        INSERT INTO employees
        (id, name, department, role, salary, status, joined_date, floor, clearance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        employees,
    )

    access_logs = [
        (1, 1, "Server Room", "2047-09-14 22:14:00", "entry"),
        (2, 6, "Server Room", "2047-09-14 22:41:00", "entry"),
        (3, 9, "Security Desk", "2047-09-14 22:45:00", "override"),
        (4, 1, "Lab 3", "2047-09-14 23:02:00", "exit"),
        (5, 6, "Server Room", "2047-09-14 23:18:00", "exit"),
    ]
    connection.executemany(
        """
        INSERT INTO access_logs
        (id, employee_id, location, timestamp, action)
        VALUES (?, ?, ?, ?, ?)
        """,
        access_logs,
    )
    connection.commit()


@router.post("")
def create_session() -> dict[str, str]:
    session_id = session_store.create_session()
    return {"session_id": session_id}


@router.post("/{session_id}/init")
def init_session(session_id: str) -> dict[str, str]:
    connection = session_store.get_connection(session_id)
    initialize_schema(connection)
    return {"status": "initialized", "session_id": session_id}


@router.post("/{session_id}/query")
def run_query(session_id: str, payload: QueryRequest) -> dict[str, list[dict[str, object]]]:
    sql = payload.sql.strip()
    if not sql.lower().startswith("select"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed.",
        )

    connection = session_store.get_connection(session_id)
    cursor = connection.execute(sql)
    rows = [dict(row) for row in cursor.fetchall()]
    return {"rows": rows}


def _project_rows(
    rows: list[dict[str, object]],
    fields: tuple[str, ...],
) -> set[tuple[object, ...]] | None:
    projected: set[tuple[object, ...]] = set()
    for row in rows:
        if any(field not in row for field in fields):
            return None
        projected.add(tuple(row[field] for field in fields))
    return projected


def _rows_have_fields(rows: list[dict[str, object]], fields: tuple[str, ...]) -> bool:
    return all(all(field in row for field in fields) for row in rows)


def _is_correct_result(level_id: str, rows: list[dict[str, object]]) -> bool:
    if level_id == "1":
        expected = {
            "Dr. Riya Sharma",
            "Marcus Holt",
            "Petra Novak",
            "Nadia Kim",
            "Leo Grant",
            "Ethan Cross",
            "Ava Patel",
            "Noah Silva",
            "Priya Das",
        }
        if len(rows) != 9:
            return False
        if not _rows_have_fields(rows, ("name", "department", "role", "status")):
            return False
        result = _project_rows(rows, ("name", "department", "role", "status"))
        if result is None:
            return False
        names = {row[0] for row in result}
        return names == expected and len(result) == 9

    if level_id == "2":
        expected = {
            ("Dr. Riya Sharma", "missing"),
            ("Ethan Cross", "suspended"),
        }
        if len(rows) != 2:
            return False
        result = _project_rows(rows, ("name", "status"))
        return result == expected

    if level_id == "3":
        expected = {
            ("Dr. Riya Sharma", "Engineering", "CLASSIFIED"),
            ("Ethan Cross", "Engineering", "HIGH"),
        }
        if len(rows) != 2:
            return False
        result = _project_rows(rows, ("name", "department", "clearance"))
        return result == expected

    if level_id == "4":
        expected = {
            (1, "Server Room", "2047-09-14 22:14:00", "entry"),
            (6, "Server Room", "2047-09-14 22:41:00", "entry"),
            (6, "Server Room", "2047-09-14 23:18:00", "exit"),
        }
        if len(rows) != 3:
            return False
        result = _project_rows(rows, ("employee_id", "location", "timestamp", "action"))
        return result == expected

    if level_id == "5":
        expected = {
            ("Marcus Holt", "Security", 1, "CLASSIFIED", "active"),
            ("Petra Novak", "Security", 1, "HIGH", "active"),
        }
        if len(rows) != 2:
            return False
        result = _project_rows(rows, ("name", "department", "floor", "clearance", "status"))
        return result == expected

    if level_id == "BONUS":
        expected = [
            (1, "2047-09-14 22:14:00"),
            (6, "2047-09-14 22:41:00"),
            (9, "2047-09-14 22:45:00"),
            (1, "2047-09-14 23:02:00"),
            (6, "2047-09-14 23:18:00"),
        ]
        if len(rows) != len(expected):
            return False
        if any("employee_id" not in row or "timestamp" not in row for row in rows):
            return False
        result = [(row["employee_id"], row["timestamp"]) for row in rows]
        return result == expected

    return False


@router.post("/{session_id}/validate")
def validate_query(
    session_id: str,
    payload: ValidateRequest,
) -> dict[str, object]:
    sql = payload.sql.strip()
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )
    if not sql.lower().startswith("select"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed.",
        )

    connection = session_store.get_connection(session_id)
    try:
        cursor = connection.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as exc:
        return {
            "rows": [],
            "error": str(exc),
            "is_correct": False,
            "level_id": payload.level_id,
        }

    return {
        "rows": rows,
        "error": None,
        "is_correct": _is_correct_result(payload.level_id, rows),
        "level_id": payload.level_id,
    }
