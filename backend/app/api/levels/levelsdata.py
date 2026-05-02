"""
Per-level content: schema DDL, seed rows per table, and canonical SQL per sublevel.

Add a new level by appending one entry to `LEVEL_CONFIGS` (ddl + tables + static_queries).
Verification compares the player's SELECT result set to the result of `static_queries[sublevel]`
on the same seeded DB — no separate `level_output` to maintain.
"""

from __future__ import annotations

from typing import TypedDict


class LevelConfig(TypedDict):
    """One playable level: in-memory SQLite schema, seed data, expected queries by sub_index."""

    ddl: str
    tables: dict[str, list[dict[str, object]]]
    static_queries: dict[int, str]


LEVEL1_DATA = {
    "employees": [
        {
            "id": 1,
            "name": "Dr. Riya Sharma",
            "department": "Engineering",
            "role": "Lead Scientist",
            "salary": 210000,
            "status": "missing",
            "joined_date": "2040-02-18",
            "floor": 3,
            "clearance": "CLASSIFIED",
        },
        {
            "id": 2,
            "name": "Marcus Holt",
            "department": "Security",
            "role": "Security Chief",
            "salary": 130000,
            "status": "active",
            "joined_date": "2038-06-01",
            "floor": 1,
            "clearance": "CLASSIFIED",
        },
        {
            "id": 3,
            "name": "Petra Novak",
            "department": "Security",
            "role": "Security Analyst",
            "salary": 98000,
            "status": "active",
            "joined_date": "2042-03-11",
            "floor": 1,
            "clearance": "HIGH",
        },
        {
            "id": 4,
            "name": "Nadia Kim",
            "department": "Engineering",
            "role": "Data Engineer",
            "salary": 125000,
            "status": "active",
            "joined_date": "2043-11-19",
            "floor": 2,
            "clearance": "HIGH",
        },
        {
            "id": 5,
            "name": "Leo Grant",
            "department": "Operations",
            "role": "Facility Manager",
            "salary": 90000,
            "status": "active",
            "joined_date": "2041-08-07",
            "floor": 1,
            "clearance": "MEDIUM",
        },
        {
            "id": 6,
            "name": "Ethan Cross",
            "department": "Engineering",
            "role": "Systems Engineer",
            "salary": 118000,
            "status": "suspended",
            "joined_date": "2041-01-15",
            "floor": 3,
            "clearance": "HIGH",
        },
        {
            "id": 7,
            "name": "Ava Patel",
            "department": "Research",
            "role": "Analyst",
            "salary": 101000,
            "status": "active",
            "joined_date": "2044-05-27",
            "floor": 4,
            "clearance": "HIGH",
        },
        {
            "id": 8,
            "name": "Noah Silva",
            "department": "IT",
            "role": "Network Engineer",
            "salary": 99000,
            "status": "active",
            "joined_date": "2040-09-14",
            "floor": 2,
            "clearance": "MEDIUM",
        },
        {
            "id": 9,
            "name": "Priya Das",
            "department": "Security",
            "role": "Shift Supervisor",
            "salary": 110000,
            "status": "active",
            "joined_date": "2039-12-30",
            "floor": 1,
            "clearance": "HIGH",
        },
    ],
    "access_logs": [
        {
            "id": 1,
            "employee_id": 1,
            "location": "Server Room",
            "timestamp": "2047-09-14 22:14:00",
            "action": "entry",
        },
        {
            "id": 2,
            "employee_id": 6,
            "location": "Server Room",
            "timestamp": "2047-09-14 22:41:00",
            "action": "entry",
        },
        {
            "id": 3,
            "employee_id": 9,
            "location": "Security Desk",
            "timestamp": "2047-09-14 22:45:00",
            "action": "override",
        },
        {
            "id": 4,
            "employee_id": 1,
            "location": "Lab 3",
            "timestamp": "2047-09-14 23:02:00",
            "action": "exit",
        },
        {
            "id": 5,
            "employee_id": 6,
            "location": "Server Room",
            "timestamp": "2047-09-14 23:18:00",
            "action": "exit",
        },
    ],
}

LEVEL1_STATIC_QUERIES: dict[int, str] = {
    1: "SELECT name, department, role, status FROM employees where status = 'missing';",
    2: "SELECT name, status FROM employees WHERE status <> 'active';",
    3: "SELECT name, department, clearance FROM employees WHERE department = 'Engineering' AND clearance IN ('HIGH', 'CLASSIFIED');",
    4: "SELECT employee_id, location, timestamp, action FROM access_logs WHERE location = 'Server Room' AND timestamp >= '2047-09-14 22:00:00';",
    5: "SELECT name, department, floor, clearance, status FROM employees WHERE department = 'Security' AND status = 'active' AND floor = 1 AND clearance IN ('HIGH', 'CLASSIFIED');",
}

LEVEL1_DDL = """
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


LEVEL_CONFIGS: dict[int, LevelConfig] = {
    1: {
        "ddl": LEVEL1_DDL,
        "tables": {
            "employees": LEVEL1_DATA["employees"],
            "access_logs": LEVEL1_DATA["access_logs"],
        },
        "static_queries": LEVEL1_STATIC_QUERIES,
    },
    # Example — uncomment and fill when level 2 exists:
    # 2: {
    #     "ddl": "...",
    #     "tables": {"some_table": [...]},
    #     "static_queries": {1: "SELECT ..."},
    # },
}
