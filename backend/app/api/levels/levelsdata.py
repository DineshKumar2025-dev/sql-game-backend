"""
Per-level content: schema DDL, seed rows per table, and canonical SQL per sublevel.

Add a new level by appending one entry to `LEVEL_CONFIGS` (ddl + tables + static_queries).
Verification compares the player's SELECT result set to the result of `static_queries[sublevel]`
on the same seeded DB — no separate `level_output` to maintain.
"""

from __future__ import annotations

from typing import NotRequired, TypedDict


class LevelConfig(TypedDict):
    """One playable level: in-memory SQLite schema, seed data, expected queries by sublevel id (e.g. l11)."""

    ddl: str
    tables: dict[str, list[dict[str, object]]]
    static_queries: dict[str, str]
    check_queries: NotRequired[dict[str, str]]


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

LEVEL1_STATIC_QUERIES: dict[str, str] = {
    "l11": "SELECT name, department, role, status FROM employees where status = 'missing';",
    "l12": "SELECT name, status FROM employees WHERE status <> 'active';",
    "l13": "SELECT name, department, clearance FROM employees WHERE department = 'Engineering' AND clearance IN ('HIGH', 'CLASSIFIED');",
    "l14": "SELECT employee_id, location, timestamp, action FROM access_logs WHERE location = 'Server Room' AND timestamp >= '2047-09-14 22:00:00';",
    "l15": "SELECT name, department, floor, clearance, status FROM employees WHERE department = 'Security' AND status = 'active' AND floor = 1 AND clearance IN ('HIGH', 'CLASSIFIED');",
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


LEVEL2_DATA = {
    "drones": [
        {"id": 1, "drone_code": "DR-001", "owner_org": "NovaCorp", "status": "active", "floor_base": 7},
        {"id": 2, "drone_code": "DR-002", "owner_org": "NovaCorp", "status": "crashed", "floor_base": 9},
        {"id": 3, "drone_code": "DR-003", "owner_org": "CityWatch", "status": "active", "floor_base": 1},
        {"id": 4, "drone_code": "DR-004", "owner_org": "BlackNet", "status": "missing", "floor_base": None},
        {"id": 5, "drone_code": "DR-005", "owner_org": "NovaCorp", "status": "active", "floor_base": 3},
    ],
    "receivers": [
        {"id": 1, "code": "RX-ALPHA", "location": "Floor 7 Lab", "org": "NovaCorp", "clearance": "HIGH"},
        {"id": 2, "code": "RX-BETA", "location": "Rooftop Array", "org": "NovaCorp", "clearance": "MEDIUM"},
        {"id": 3, "code": "RX-GAMMA", "location": "Underground Bunker", "org": "BlackNet", "clearance": "CLASSIFIED"},
        {"id": 4, "code": "RX-DELTA", "location": "City Tower", "org": "CityWatch", "clearance": "LOW"},
        {"id": 5, "code": "RX-OMEGA", "location": "Unknown", "org": "Unknown", "clearance": "CLASSIFIED"},
    ],
    "transmissions": [
        {
            "id": 1,
            "drone_id": 2,
            "receiver_id": 1,
            "signal_strength": 88,
            "payload_size": 1240,
            "timestamp": "2051-03-10 21:10:00",
            "encrypted": 0,
        },
        {
            "id": 2,
            "drone_id": 2,
            "receiver_id": 3,
            "signal_strength": 72,
            "payload_size": 890,
            "timestamp": "2051-03-10 21:45:00",
            "encrypted": 1,
        },
        {
            "id": 3,
            "drone_id": 2,
            "receiver_id": 5,
            "signal_strength": 91,
            "payload_size": 2100,
            "timestamp": "2051-03-10 22:00:00",
            "encrypted": 1,
        },
        {
            "id": 4,
            "drone_id": 2,
            "receiver_id": 2,
            "signal_strength": 60,
            "payload_size": 540,
            "timestamp": "2051-03-10 22:18:00",
            "encrypted": 0,
        },
        {
            "id": 5,
            "drone_id": 2,
            "receiver_id": 5,
            "signal_strength": 95,
            "payload_size": 3800,
            "timestamp": "2051-03-10 23:47:00",
            "encrypted": 1,
        },
        {
            "id": 6,
            "drone_id": 2,
            "receiver_id": 3,
            "signal_strength": 44,
            "payload_size": 220,
            "timestamp": "2051-03-11 00:02:00",
            "encrypted": 1,
        },
        {
            "id": 7,
            "drone_id": 2,
            "receiver_id": 1,
            "signal_strength": 30,
            "payload_size": 180,
            "timestamp": "2051-03-11 00:15:00",
            "encrypted": 0,
        },
        {
            "id": 8,
            "drone_id": 1,
            "receiver_id": 4,
            "signal_strength": 80,
            "payload_size": 900,
            "timestamp": "2051-03-10 20:00:00",
            "encrypted": 0,
        },
        {
            "id": 9,
            "drone_id": 3,
            "receiver_id": 4,
            "signal_strength": 70,
            "payload_size": 600,
            "timestamp": "2051-03-10 19:00:00",
            "encrypted": 0,
        },
    ],
}

LEVEL2_STATIC_QUERIES: dict[str, str] = {
    "l21": "SELECT * FROM transmissions WHERE drone_id = 2 ORDER BY timestamp ASC;",
    "l22": "SELECT id, receiver_id, payload_size, timestamp FROM transmissions WHERE drone_id = 2 ORDER BY timestamp DESC;",
    "l23": "SELECT id, receiver_id, payload_size, timestamp, encrypted FROM transmissions WHERE drone_id = 2 ORDER BY timestamp DESC LIMIT 1;",
    "l24": "SELECT id, receiver_id, payload_size, timestamp, encrypted FROM transmissions WHERE drone_id = 2 ORDER BY payload_size DESC LIMIT 3;",
    "l25": "SELECT id, receiver_id, payload_size, timestamp FROM transmissions WHERE drone_id = 2 AND encrypted = 1 ORDER BY payload_size DESC;",
    "l26": "SELECT id, receiver_id, signal_strength, timestamp FROM transmissions WHERE drone_id = 2 ORDER BY signal_strength ASC LIMIT 3;",
}

LEVEL2_DDL = """
CREATE TABLE drones (
    id INTEGER PRIMARY KEY,
    drone_code TEXT,
    owner_org TEXT,
    status TEXT,
    floor_base INTEGER
);

CREATE TABLE receivers (
    id INTEGER PRIMARY KEY,
    code TEXT,
    location TEXT,
    org TEXT,
    clearance TEXT
);

CREATE TABLE transmissions (
    id INTEGER PRIMARY KEY,
    drone_id INTEGER,
    receiver_id INTEGER,
    signal_strength INTEGER,
    payload_size INTEGER,
    timestamp TEXT,
    encrypted INTEGER,
    FOREIGN KEY (drone_id) REFERENCES drones(id),
    FOREIGN KEY (receiver_id) REFERENCES receivers(id)
);
"""

LEVEL3_DATA = {
    "suspects": [
        {"id": 1, "name": "Marcus Veil", "alias": "GHOST", "org": "NexusVoid", "threat_level": "CRITICAL"},
        {"id": 2, "name": "Lena Cross", "alias": "PHANTOM", "org": "BlackNet", "threat_level": "HIGH"},
        {"id": 3, "name": "Jin Rat", "alias": "RODENT", "org": "Unknown", "threat_level": "MEDIUM"},
        {"id": 4, "name": "Dr. Riya Sharma", "alias": "ORACLE", "org": "NovaCorp", "threat_level": "HIGH"},
        {"id": 5, "name": "Victor Crane", "alias": "APEX", "org": "NovaCorp", "threat_level": "CRITICAL"},
        {"id": 6, "name": "Dana Wolfe", "alias": "FOX", "org": "CityGov", "threat_level": "LOW"},
        {"id": 7, "name": "Sable Mox", "alias": "SHADOW", "org": "NexusVoid", "threat_level": "HIGH"},
    ],
    "items_catalog": [
        {"id": 1, "item_name": "ORACLE Source Code", "category": "corporate", "risk_level": "CRITICAL"},
        {"id": 2, "item_name": "Biometric Master Key", "category": "biodata", "risk_level": "CRITICAL"},
        {"id": 3, "item_name": "City Admin Credentials", "category": "credentials", "risk_level": "HIGH"},
        {"id": 4, "item_name": "Surveillance Bypass", "category": "credentials", "risk_level": "HIGH"},
        {"id": 5, "item_name": "Citizen DNA Archive", "category": "biodata", "risk_level": "HIGH"},
    ],
    "transactions": [
        {
            "id": 1,
            "seller_id": 1,
            "buyer_id": 2,
            "item": "ORACLE Source Code",
            "price_cr": 85000,
            "date": "2051-03-11",
            "status": "completed",
        },
        {
            "id": 2,
            "seller_id": 1,
            "buyer_id": 5,
            "item": "Biometric Master Key",
            "price_cr": 120000,
            "date": "2051-03-11",
            "status": "completed",
        },
        {
            "id": 3,
            "seller_id": 7,
            "buyer_id": 3,
            "item": "City Admin Credentials",
            "price_cr": 40000,
            "date": "2051-03-10",
            "status": "flagged",
        },
        {
            "id": 4,
            "seller_id": 2,
            "buyer_id": 5,
            "item": "Surveillance Bypass",
            "price_cr": 55000,
            "date": "2051-03-12",
            "status": "completed",
        },
        {
            "id": 5,
            "seller_id": 1,
            "buyer_id": 6,
            "item": "Citizen DNA Archive",
            "price_cr": 30000,
            "date": "2051-03-09",
            "status": "pending",
        },
        {
            "id": 6,
            "seller_id": 7,
            "buyer_id": 2,
            "item": "ORACLE Source Code",
            "price_cr": 90000,
            "date": "2051-03-12",
            "status": "completed",
        },
        {
            "id": 7,
            "seller_id": 5,
            "buyer_id": 1,
            "item": "Biometric Master Key",
            "price_cr": 110000,
            "date": "2051-03-13",
            "status": "flagged",
        },
    ],
}

LEVEL3_STATIC_QUERIES: dict[str, str] = {
    "l31": (
        "SELECT t.id, s.name AS seller, t.item, t.price_cr, t.date "
        "FROM transactions t "
        "JOIN suspects s ON t.seller_id = s.id "
        "ORDER BY t.date;"
    ),
    "l32": (
        "SELECT t.id, s.name AS buyer, t.item, t.price_cr, t.status "
        "FROM transactions t "
        "JOIN suspects s ON t.buyer_id = s.id "
        "ORDER BY t.price_cr DESC;"
    ),
    "l33": (
        "SELECT t.id, seller.name AS seller, buyer.name AS buyer, t.item, t.price_cr, t.status "
        "FROM transactions t "
        "JOIN suspects seller ON t.seller_id = seller.id "
        "JOIN suspects buyer ON t.buyer_id = buyer.id "
        "ORDER BY t.date;"
    ),
    "l34": (
        "SELECT seller.name AS seller, buyer.name AS buyer, t.item, t.price_cr, t.date "
        "FROM transactions t "
        "JOIN suspects seller ON t.seller_id = seller.id "
        "JOIN suspects buyer ON t.buyer_id = buyer.id "
        "WHERE t.status = 'flagged';"
    ),
    "l35": (
        "SELECT seller.name AS seller, buyer.name AS buyer, t.price_cr, t.date, t.status "
        "FROM transactions t "
        "JOIN suspects seller ON t.seller_id = seller.id "
        "JOIN suspects buyer ON t.buyer_id = buyer.id "
        "WHERE t.item = 'ORACLE Source Code' "
        "ORDER BY t.date;"
    ),
    "l36": (
        "SELECT seller.name AS seller, seller.threat_level AS seller_threat, "
        "buyer.name AS buyer, buyer.threat_level AS buyer_threat, t.item, t.price_cr "
        "FROM transactions t "
        "JOIN suspects seller ON t.seller_id = seller.id "
        "JOIN suspects buyer ON t.buyer_id = buyer.id "
        "WHERE seller.threat_level = 'CRITICAL' OR buyer.threat_level = 'CRITICAL' "
        "ORDER BY t.price_cr DESC;"
    ),
}

LEVEL3_DDL = """
CREATE TABLE suspects (
    id INTEGER PRIMARY KEY,
    name TEXT,
    alias TEXT,
    org TEXT,
    threat_level TEXT
);

CREATE TABLE items_catalog (
    id INTEGER PRIMARY KEY,
    item_name TEXT,
    category TEXT,
    risk_level TEXT
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    seller_id INTEGER,
    buyer_id INTEGER,
    item TEXT,
    price_cr INTEGER,
    date TEXT,
    status TEXT,
    FOREIGN KEY (seller_id) REFERENCES suspects(id),
    FOREIGN KEY (buyer_id) REFERENCES suspects(id)
);
"""

LEVEL4_DATA = {
    "accounts": [
        {"id": 1, "holder": "Victor Crane", "org": "NovaCorp", "account_type": "corporate", "created_at": "2045-01-01"},
        {"id": 2, "holder": "Ghost Acct A", "org": "NexusVoid", "account_type": "ghost", "created_at": "2051-01-15"},
        {"id": 3, "holder": "Ghost Acct B", "org": "NexusVoid", "account_type": "ghost", "created_at": "2051-01-16"},
        {"id": 4, "holder": "Dana Wolfe", "org": "CityGov", "account_type": "personal", "created_at": "2048-06-01"},
        {"id": 5, "holder": "Marcus Veil", "org": "NexusVoid", "account_type": "corporate", "created_at": "2049-03-10"},
        {"id": 6, "holder": "Ghost Acct C", "org": "Unknown", "account_type": "ghost", "created_at": "2051-02-01"},
        {"id": 7, "holder": "Lena Cross", "org": "BlackNet", "account_type": "corporate", "created_at": "2050-07-22"},
    ],
    "bank_transactions": [
        {"id": 1, "account_id": 2, "amount": -500, "category": "transfer", "date": "2051-03-10", "flagged": 1},
        {"id": 2, "account_id": 2, "amount": -500, "category": "transfer", "date": "2051-03-10", "flagged": 1},
        {"id": 3, "account_id": 2, "amount": -500, "category": "transfer", "date": "2051-03-11", "flagged": 1},
        {"id": 4, "account_id": 3, "amount": -750, "category": "transfer", "date": "2051-03-10", "flagged": 1},
        {"id": 5, "account_id": 3, "amount": -750, "category": "transfer", "date": "2051-03-11", "flagged": 1},
        {"id": 6, "account_id": 6, "amount": -300, "category": "transfer", "date": "2051-03-11", "flagged": 1},
        {"id": 7, "account_id": 6, "amount": -300, "category": "transfer", "date": "2051-03-11", "flagged": 1},
        {"id": 8, "account_id": 6, "amount": -300, "category": "transfer", "date": "2051-03-12", "flagged": 1},
        {"id": 9, "account_id": 1, "amount": -50000, "category": "investment", "date": "2051-03-11", "flagged": 0},
        {"id": 10, "account_id": 4, "amount": 8000, "category": "salary", "date": "2051-03-10", "flagged": 0},
        {"id": 11, "account_id": 5, "amount": -25000, "category": "consulting", "date": "2051-03-12", "flagged": 0},
        {"id": 12, "account_id": 7, "amount": -15000, "category": "services", "date": "2051-03-12", "flagged": 0},
        {"id": 13, "account_id": 2, "amount": -500, "category": "transfer", "date": "2051-03-12", "flagged": 1},
        {"id": 14, "account_id": 3, "amount": -750, "category": "transfer", "date": "2051-03-12", "flagged": 1},
        {"id": 15, "account_id": 6, "amount": -300, "category": "transfer", "date": "2051-03-13", "flagged": 1},
    ],
}

LEVEL4_STATIC_QUERIES: dict[str, str] = {
    "l41": (
        "SELECT account_id, COUNT(*) AS total_transactions "
        "FROM bank_transactions "
        "GROUP BY account_id "
        "ORDER BY total_transactions DESC;"
    ),
    "l42": (
        "SELECT account_id, SUM(amount) AS total_outflow "
        "FROM bank_transactions "
        "WHERE amount < 0 "
        "GROUP BY account_id "
        "ORDER BY total_outflow ASC;"
    ),
    "l43": (
        "SELECT account_id, COUNT(*) AS tx_count "
        "FROM bank_transactions "
        "GROUP BY account_id "
        "HAVING COUNT(*) > 3 "
        "ORDER BY tx_count DESC;"
    ),
    "l44": (
        "SELECT account_id, COUNT(*) AS flagged_count, SUM(amount) AS flagged_total "
        "FROM bank_transactions "
        "WHERE flagged = 1 "
        "GROUP BY account_id "
        "ORDER BY flagged_count DESC;"
    ),
    "l45": (
        "SELECT category, COUNT(*) AS count, AVG(amount) AS avg_amount, SUM(amount) AS total "
        "FROM bank_transactions "
        "GROUP BY category "
        "ORDER BY total ASC;"
    ),
    "l46": (
        "SELECT a.org, COUNT(bt.id) AS transactions, SUM(bt.amount) AS total_flow "
        "FROM bank_transactions bt "
        "JOIN accounts a ON bt.account_id = a.id "
        "WHERE bt.amount < 0 "
        "GROUP BY a.org "
        "HAVING SUM(bt.amount) < -1000 "
        "ORDER BY total_flow ASC;"
    ),
}

LEVEL4_DDL = """
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    holder TEXT,
    org TEXT,
    account_type TEXT,
    created_at TEXT
);

CREATE TABLE bank_transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER,
    amount INTEGER,
    category TEXT,
    date TEXT,
    flagged INTEGER,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
"""

LEVEL5_DATA = {
    "agents": [
        {"id": 1, "codename": "APEX", "real_name": "Victor Crane", "reports_to": None, "salary": 500000, "active": 1},
        {"id": 2, "codename": "GHOST", "real_name": "Marcus Veil", "reports_to": 1, "salary": 120000, "active": 1},
        {"id": 3, "codename": "PHANTOM", "real_name": "Lena Cross", "reports_to": 2, "salary": 95000, "active": 1},
        {"id": 4, "codename": "RODENT", "real_name": "Jin Rat", "reports_to": 3, "salary": 40000, "active": 1},
        {"id": 5, "codename": "SHADOW", "real_name": "Sable Mox", "reports_to": 2, "salary": 85000, "active": 1},
        {"id": 6, "codename": "FOX", "real_name": None, "reports_to": 3, "salary": 55000, "active": 1},
        {"id": 7, "codename": "WRAITH", "real_name": None, "reports_to": 5, "salary": 45000, "active": 0},
    ],
    "orders": [
        {"id": 1, "issued_by": 2, "target": "Dr. Riya Sharma", "operation": "Kidnap", "priority": "CRITICAL", "date": "2051-03-10"},
        {"id": 2, "issued_by": 3, "target": "NovaCorp Server", "operation": "Data Extraction", "priority": "HIGH", "date": "2051-03-10"},
        {"id": 3, "issued_by": 4, "target": "DroneNet", "operation": "Signal Intercept", "priority": "MEDIUM", "date": "2051-03-11"},
        {"id": 4, "issued_by": 5, "target": "City Treasury", "operation": "Ghost Transfers", "priority": "HIGH", "date": "2051-03-11"},
        {"id": 5, "issued_by": 2, "target": "ORACLE Files", "operation": "Data Sale", "priority": "CRITICAL", "date": "2051-03-12"},
        {"id": 6, "issued_by": 1, "target": "NexusVoid", "operation": "Network Expansion", "priority": "LOW", "date": "2051-03-09"},
        {"id": 7, "issued_by": 6, "target": "CityWatch Cameras", "operation": "Disable", "priority": "HIGH", "date": "2051-03-12"},
    ],
}

LEVEL5_STATIC_QUERIES: dict[str, str] = {
    "l51": (
        "SELECT codename, real_name, salary "
        "FROM agents "
        "WHERE salary > (SELECT AVG(salary) FROM agents) "
        "ORDER BY salary DESC;"
    ),
    "l52": (
        "SELECT codename, real_name "
        "FROM agents "
        "WHERE id IN (SELECT issued_by FROM orders WHERE priority = 'CRITICAL');"
    ),
    "l53": (
        "SELECT codename, real_name, salary "
        "FROM agents "
        "WHERE reports_to = (SELECT id FROM agents ORDER BY salary DESC LIMIT 1);"
    ),
    "l54": (
        "SELECT o.operation, o.target, o.priority, o.date "
        "FROM orders o "
        "WHERE o.issued_by IN (SELECT id FROM agents WHERE salary > 100000) "
        "ORDER BY o.date;"
    ),
    "l55": (
        "SELECT codename, real_name "
        "FROM agents "
        "WHERE active = 0 AND id NOT IN (SELECT DISTINCT issued_by FROM orders);"
    ),
    "l56": (
        "SELECT codename, real_name, reports_to "
        "FROM agents "
        "WHERE reports_to IN ("
        "  SELECT id FROM agents WHERE reports_to = (SELECT id FROM agents WHERE codename = 'APEX')"
        ") "
        "OR reports_to = (SELECT id FROM agents WHERE codename = 'APEX');"
    ),
}

LEVEL5_DDL = """
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    codename TEXT,
    real_name TEXT,
    reports_to INTEGER,
    salary INTEGER,
    active INTEGER,
    FOREIGN KEY (reports_to) REFERENCES agents(id)
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    issued_by INTEGER,
    target TEXT,
    operation TEXT,
    priority TEXT,
    date TEXT,
    FOREIGN KEY (issued_by) REFERENCES agents(id)
);
"""

LEVEL6_DATA = {
    # Reuse the proxy network agents so Level 6 can JOIN to identify the key holder.
    "agents": LEVEL5_DATA["agents"],
    "memory_files": [
        {"id": 1, "owner_id": 1, "file_name": "riya_mem_2051.nrf", "size_mb": 420, "encrypted": 1, "key_id": 3, "archive_node": "NODE-7"},
        {"id": 2, "owner_id": 2, "file_name": "sharma_lab_notes.nrf", "size_mb": 180, "encrypted": 1, "key_id": 3, "archive_node": "NODE-7"},
        {"id": 3, "owner_id": 3, "file_name": "oracle_design.nrf", "size_mb": 560, "encrypted": 1, "key_id": 3, "archive_node": "NODE-7"},
        {"id": 4, "owner_id": 4, "file_name": "routine_backup.nrf", "size_mb": 90, "encrypted": 0, "key_id": None, "archive_node": "NODE-2"},
        {"id": 5, "owner_id": 5, "file_name": "personal_log.nrf", "size_mb": 110, "encrypted": 0, "key_id": None, "archive_node": "NODE-2"},
    ],
    "encryption_keys": [
        {"id": 1, "key_code": "KEY-ALPHA-001", "issued_to": 6, "valid": 1, "created_at": "2051-01-01"},
        {"id": 2, "key_code": "KEY-BETA-002", "issued_to": 4, "valid": 1, "created_at": "2051-02-15"},
        {"id": 3, "key_code": "KEY-GAMMA-003", "issued_to": 1, "valid": 1, "created_at": "2051-03-10"},
        {"id": 4, "key_code": "KEY-DELTA-004", "issued_to": 7, "valid": 0, "created_at": "2051-03-01"},
    ],
    "archive_sessions": [
        {"id": 1, "agent_id": 1, "node": "NODE-7", "action": "READ", "file_id": 1, "timestamp": "2051-03-10 22:00:00"},
        {"id": 2, "agent_id": 1, "node": "NODE-7", "action": "READ", "file_id": 2, "timestamp": "2051-03-10 22:05:00"},
        {"id": 3, "agent_id": 1, "node": "NODE-7", "action": "READ", "file_id": 3, "timestamp": "2051-03-10 22:10:00"},
        {"id": 4, "agent_id": 1, "node": "NODE-7", "action": "ENCRYPT", "file_id": 1, "timestamp": "2051-03-10 22:30:00"},
        {"id": 5, "agent_id": 1, "node": "NODE-7", "action": "ENCRYPT", "file_id": 2, "timestamp": "2051-03-10 22:31:00"},
        {"id": 6, "agent_id": 1, "node": "NODE-7", "action": "ENCRYPT", "file_id": 3, "timestamp": "2051-03-10 22:32:00"},
        {"id": 7, "agent_id": 1, "node": "NODE-7", "action": "COPY", "file_id": 1, "timestamp": "2051-03-10 23:00:00"},
        {"id": 8, "agent_id": 1, "node": "NODE-7", "action": "COPY", "file_id": 2, "timestamp": "2051-03-10 23:01:00"},
        {"id": 9, "agent_id": 1, "node": "NODE-7", "action": "COPY", "file_id": 3, "timestamp": "2051-03-10 23:02:00"},
        {"id": 10, "agent_id": 2, "node": "NODE-2", "action": "READ", "file_id": 4, "timestamp": "2051-03-10 20:00:00"},
    ],
}

LEVEL6_STATIC_QUERIES: dict[str, str] = {
    "l61": (
        "WITH encrypted_files AS ("
        "  SELECT id, file_name, size_mb, key_id, archive_node "
        "  FROM memory_files "
        "  WHERE encrypted = 1"
        ") "
        "SELECT * FROM encrypted_files;"
    ),
    "l62": (
        "WITH key_holder AS ("
        "  SELECT issued_to, key_code "
        "  FROM encryption_keys "
        "  WHERE id = 3 AND valid = 1"
        ") "
        "SELECT a.codename, a.real_name, kh.key_code "
        "FROM agents a "
        "JOIN key_holder kh ON a.id = kh.issued_to;"
    ),
    "l63": (
        "WITH node7_sessions AS ("
        "  SELECT id, agent_id, action, file_id, timestamp "
        "  FROM archive_sessions "
        "  WHERE node = 'NODE-7'"
        ") "
        "SELECT * FROM node7_sessions "
        "ORDER BY timestamp;"
    ),
    "l64": (
        "WITH copy_sessions AS ("
        "  SELECT file_id, timestamp "
        "  FROM archive_sessions "
        "  WHERE action = 'COPY'"
        "), "
        "copied_files AS ("
        "  SELECT mf.file_name, mf.size_mb, cs.timestamp "
        "  FROM memory_files mf "
        "  JOIN copy_sessions cs ON mf.id = cs.file_id"
        ") "
        "SELECT * FROM copied_files "
        "ORDER BY timestamp;"
    ),
    "l65": (
        "WITH stolen AS ("
        "  SELECT mf.archive_node, mf.size_mb "
        "  FROM memory_files mf "
        "  JOIN archive_sessions ars ON mf.id = ars.file_id "
        "  WHERE ars.action = 'COPY'"
        ") "
        "SELECT archive_node, COUNT(*) AS files_stolen, SUM(size_mb) AS total_mb "
        "FROM stolen "
        "GROUP BY archive_node;"
    ),
    "l66": (
        "WITH attack_sessions AS ("
        "  SELECT agent_id, action, file_id, timestamp "
        "  FROM archive_sessions "
        "  WHERE node = 'NODE-7'"
        "), "
        "stolen_files AS ("
        "  SELECT mf.file_name, mf.size_mb, mf.key_id, ars.timestamp "
        "  FROM memory_files mf "
        "  JOIN attack_sessions ars ON mf.id = ars.file_id "
        "  WHERE ars.action = 'COPY'"
        "), "
        "key_info AS ("
        "  SELECT id, key_code, issued_to "
        "  FROM encryption_keys "
        "  WHERE id = 3"
        ") "
        "SELECT sf.file_name, sf.size_mb, ki.key_code, sf.timestamp "
        "FROM stolen_files sf "
        "CROSS JOIN key_info ki "
        "ORDER BY sf.timestamp;"
    ),
}

LEVEL6_DDL = """
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    codename TEXT,
    real_name TEXT,
    reports_to INTEGER,
    salary INTEGER,
    active INTEGER,
    FOREIGN KEY (reports_to) REFERENCES agents(id)
);

CREATE TABLE memory_files (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER,
    file_name TEXT,
    size_mb INTEGER,
    encrypted INTEGER,
    key_id INTEGER,
    archive_node TEXT
);

CREATE TABLE encryption_keys (
    id INTEGER PRIMARY KEY,
    key_code TEXT,
    issued_to INTEGER,
    valid INTEGER,
    created_at TEXT
);

CREATE TABLE archive_sessions (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER,
    node TEXT,
    action TEXT,
    file_id INTEGER,
    timestamp TEXT
);
"""

LEVEL7_DATA = {
    "evidence": [
        {"id": 1, "case_id": 3, "description": "Drone transmission logs", "verified": 1, "planted": 0, "added_by": "AXEL-7", "date_added": "2051-03-11"},
        {"id": 2, "case_id": 3, "description": "Ghost account records", "verified": 1, "planted": 0, "added_by": "AXEL-7", "date_added": "2051-03-11"},
        {"id": 3, "case_id": 3, "description": "Victor Crane alibi confirmed", "verified": 0, "planted": 1, "added_by": "MOLE", "date_added": "2051-03-12"},
        {"id": 4, "case_id": 3, "description": "NexusVoid contract deleted", "verified": 0, "planted": 1, "added_by": "MOLE", "date_added": "2051-03-12"},
        {"id": 5, "case_id": 3, "description": "Marcus Veil location: home", "verified": 0, "planted": 1, "added_by": "MOLE", "date_added": "2051-03-12"},
    ],
    "witnesses": [
        {"id": 1, "name": "Dr. Leena Park", "testimony": "Saw Ethan Cross in server room", "credibility": "HIGH", "protected": 1},
        {"id": 2, "name": "Jin Tao", "testimony": "Nothing suspicious that night", "credibility": "FABRICATED", "protected": 0},
        {"id": 3, "name": "Tom Briggs", "testimony": "Heard voices on Floor 7", "credibility": "MEDIUM", "protected": 1},
        {"id": 4, "name": "Petra Novak", "testimony": "Was off duty all night", "credibility": "FABRICATED", "protected": 0},
    ],
}

LEVEL7_STATIC_QUERIES: dict[str, str] = {
    "l71": (
        "SELECT * FROM evidence WHERE planted = 1; "
        "SELECT * FROM witnesses WHERE credibility = 'FABRICATED';"
    ),
    "l72": "DELETE FROM evidence WHERE planted = 1;",
    "l73": "DELETE FROM witnesses WHERE credibility = 'FABRICATED';",
    "l74": (
        "INSERT INTO evidence (case_id, description, verified, planted, added_by, date_added) "
        "VALUES (3, 'NexusVoid contract — signed by Victor Crane', 1, 0, 'AXEL-7', '2051-03-13');"
    ),
    "l75": (
        "INSERT INTO witnesses (name, testimony, credibility, protected) "
        "VALUES ('Dr. Riya Sharma', 'Victor Crane ordered my disappearance to prevent ORACLE testimony', 'HIGH', 1);"
    ),
    "l76": (
        "UPDATE evidence SET verified = 1 "
        "WHERE added_by = 'AXEL-7' AND verified = 0;"
    ),
}

LEVEL7_CHECK_QUERIES: dict[str, str] = {
    "l71": (
        "SELECT 'evidence' AS source, id, description, planted, verified "
        "FROM evidence WHERE planted = 1 "
        "UNION ALL "
        "SELECT 'witnesses' AS source, id, name AS description, 0 AS planted, 0 AS verified "
        "FROM witnesses WHERE credibility = 'FABRICATED' "
        "ORDER BY source, id;"
    ),
    "l72": "SELECT COUNT(*) AS planted_remaining FROM evidence WHERE planted = 1;",
    "l73": "SELECT COUNT(*) AS fabricated_remaining FROM witnesses WHERE credibility = 'FABRICATED';",
    "l74": "SELECT description, verified, planted, added_by, date_added FROM evidence WHERE description LIKE 'NexusVoid contract%';",
    "l75": "SELECT name, credibility, protected FROM witnesses WHERE name = 'Dr. Riya Sharma';",
    "l76": "SELECT COUNT(*) AS unverified_axel7 FROM evidence WHERE added_by = 'AXEL-7' AND verified = 0;",
}

LEVEL7_DDL = """
CREATE TABLE evidence (
    id INTEGER PRIMARY KEY,
    case_id INTEGER,
    description TEXT,
    verified INTEGER,
    planted INTEGER,
    added_by TEXT,
    date_added TEXT
);

CREATE TABLE witnesses (
    id INTEGER PRIMARY KEY,
    name TEXT,
    testimony TEXT,
    credibility TEXT,
    protected INTEGER
);
"""

LEVEL8_DATA = {
    "balances": [
        {"id": 1, "account": "CityTreasury", "balance": 5000000, "last_updated": "2051-03-13 08:00:00"},
        {"id": 2, "account": "NovaCorp-Payroll", "balance": 200000, "last_updated": "2051-03-13 08:00:00"},
        {"id": 3, "account": "Crane-Offshore", "balance": 0, "last_updated": "2051-03-13 08:00:00"},
        {"id": 4, "account": "Staff-Accounts", "balance": 150000, "last_updated": "2051-03-13 08:00:00"},
    ],
    "ledger": [
        {"id": 1, "account_from": "CityTreasury", "account_to": "NovaCorp-Payroll", "amount": 200000, "status": "valid", "timestamp": "2051-03-13 09:00:00", "tx_group": 1},
        {"id": 2, "account_from": "CityTreasury", "account_to": "Crane-Offshore", "amount": 2000000, "status": "ghost", "timestamp": "2051-03-13 09:00:01", "tx_group": 1},
        {"id": 3, "account_from": "NovaCorp-Payroll", "account_to": "Staff-Accounts", "amount": 150000, "status": "valid", "timestamp": "2051-03-13 09:05:00", "tx_group": 2},
        {"id": 4, "account_from": "Crane-Offshore", "account_to": "Unknown-Vault", "amount": 2000000, "status": "ghost", "timestamp": "2051-03-13 09:10:00", "tx_group": 3},
    ],
}

LEVEL8_STATIC_QUERIES: dict[str, str] = {
    "l81": "SELECT * FROM ledger WHERE status = 'ghost' ORDER BY timestamp;",
    "l82": "SELECT account, balance FROM balances ORDER BY balance DESC;",
    "l83": (
        "BEGIN; "
        "UPDATE ledger SET status = 'reversed' WHERE status = 'ghost'; "
        "SELECT * FROM ledger; "
        "COMMIT;"
    ),
    "l84": (
        "BEGIN; "
        "UPDATE balances SET balance = 0, last_updated = '2051-03-13 10:00:00' "
        "WHERE account = 'Crane-Offshore'; "
        "COMMIT;"
    ),
    "l85": (
        "BEGIN; "
        "DELETE FROM ledger WHERE status = 'valid'; "
        "SELECT * FROM ledger; "
        "ROLLBACK; "
        "SELECT * FROM ledger;"
    ),
    "l86": (
        "SELECT status, COUNT(*) AS count, SUM(amount) AS total_amount "
        "FROM ledger "
        "GROUP BY status "
        "ORDER BY total_amount DESC;"
    ),
}

LEVEL8_CHECK_QUERIES: dict[str, str] = {
    "l81": "SELECT id, account_from, account_to, amount, status, timestamp, tx_group FROM ledger WHERE status = 'ghost' ORDER BY timestamp;",
    "l82": "SELECT account, balance FROM balances ORDER BY balance DESC;",
    # after reversal, no ghosts remain
    "l83": "SELECT status, COUNT(*) AS count FROM ledger GROUP BY status ORDER BY status;",
    "l84": "SELECT account, balance, last_updated FROM balances WHERE account = 'Crane-Offshore';",
    # after rollback, ledger unchanged from seed
    "l85": "SELECT id, account_from, account_to, amount, status, timestamp, tx_group FROM ledger ORDER BY id;",
    "l86": "SELECT status, COUNT(*) AS count, SUM(amount) AS total_amount FROM ledger GROUP BY status ORDER BY total_amount DESC;",
}

LEVEL8_DDL = """
CREATE TABLE ledger (
    id INTEGER PRIMARY KEY,
    account_from TEXT,
    account_to TEXT,
    amount INTEGER,
    status TEXT,
    timestamp TEXT,
    tx_group INTEGER
);

CREATE TABLE balances (
    id INTEGER PRIMARY KEY,
    account TEXT UNIQUE,
    balance INTEGER,
    last_updated TEXT
);
"""

LEVEL9_DATA = {
    "citizens": [
        {"id": 1, "name": "Victor Crane", "district": "Central", "threat_flag": 1, "last_seen": "2051-03-13 09:00:00"},
        {"id": 2, "name": "Marcus Veil", "district": "NorthGrid", "threat_flag": 1, "last_seen": "2051-03-12 23:00:00"},
        {"id": 3, "name": "Lena Cross", "district": "DockZone", "threat_flag": 1, "last_seen": "2051-03-13 01:00:00"},
        {"id": 4, "name": "Dana Wolfe", "district": "Central", "threat_flag": 0, "last_seen": "2051-03-13 08:00:00"},
        {"id": 5, "name": "Jin Rat", "district": "SouthBlock", "threat_flag": 1, "last_seen": "2051-03-13 02:00:00"},
    ],
    "incidents": [
        {"id": 1, "citizen_id": 1, "type": "Unauthorized Access", "district": "Central", "severity": "CRITICAL", "timestamp": "2051-03-13 09:05:00", "resolved": 0},
        {"id": 2, "citizen_id": 2, "type": "Data Theft", "district": "NorthGrid", "severity": "HIGH", "timestamp": "2051-03-12 23:10:00", "resolved": 0},
        {"id": 3, "citizen_id": 3, "type": "Smuggling", "district": "DockZone", "severity": "HIGH", "timestamp": "2051-03-13 01:15:00", "resolved": 0},
        {"id": 4, "citizen_id": 4, "type": "Noise Complaint", "district": "Central", "severity": "LOW", "timestamp": "2051-03-13 08:30:00", "resolved": 1},
        {"id": 5, "citizen_id": 5, "type": "Suspicious Activity", "district": "SouthBlock", "severity": "MEDIUM", "timestamp": "2051-03-13 02:00:00", "resolved": 0},
        {"id": 6, "citizen_id": 1, "type": "Bribery", "district": "Central", "severity": "CRITICAL", "timestamp": "2051-03-13 09:30:00", "resolved": 0},
    ],
    "query_log": [
        {"id": 1, "query_text": "SELECT * FROM incidents WHERE district = 'Central'", "exec_time_ms": 38400, "ran_at": "2051-03-13 09:00:00", "used_index": 0},
        {"id": 2, "query_text": "SELECT * FROM citizens WHERE threat_flag = true", "exec_time_ms": 41200, "ran_at": "2051-03-13 09:01:00", "used_index": 0},
        {"id": 3, "query_text": "SELECT * FROM incidents WHERE severity = 'CRITICAL'", "exec_time_ms": 35800, "ran_at": "2051-03-13 09:02:00", "used_index": 0},
        {"id": 4, "query_text": "SELECT * FROM citizens WHERE district = 'NorthGrid'", "exec_time_ms": 39100, "ran_at": "2051-03-13 09:03:00", "used_index": 0},
    ],
}

LEVEL9_STATIC_QUERIES: dict[str, str] = {
    "l91": (
        "SELECT id, query_text, exec_time_ms "
        "FROM query_log "
        "WHERE exec_time_ms > 30000 AND used_index = 0 "
        "ORDER BY exec_time_ms DESC;"
    ),
    "l92": "EXPLAIN SELECT * FROM incidents WHERE district = 'Central';",
    "l93": "CREATE INDEX idx_incidents_district ON incidents(district);",
    "l94": "CREATE INDEX idx_citizens_threat ON citizens(threat_flag); EXPLAIN SELECT * FROM citizens WHERE threat_flag = 1;",
    "l95": "CREATE INDEX idx_incidents_severity_district ON incidents(severity, district); EXPLAIN SELECT * FROM incidents WHERE severity = 'CRITICAL' AND district = 'Central';",
    "l96": (
        "SELECT c.name, c.district, i.type, i.severity, i.timestamp "
        "FROM incidents i "
        "JOIN citizens c ON i.citizen_id = c.id "
        "WHERE i.severity = 'CRITICAL' AND i.resolved = 0 AND c.threat_flag = 1 "
        "ORDER BY i.timestamp;"
    ),
    "l97": (
        "INSERT INTO query_log (query_text, exec_time_ms, ran_at, used_index) "
        "VALUES ('SELECT * FROM incidents WHERE district = ''Central''', 12, '2051-03-13 10:00:00', 1); "
        "SELECT query_text, exec_time_ms, used_index FROM query_log ORDER BY ran_at DESC LIMIT 2;"
    ),
}

LEVEL9_CHECK_QUERIES: dict[str, str] = {
    "l91": (
        "SELECT id, query_text, exec_time_ms "
        "FROM query_log "
        "WHERE exec_time_ms > 30000 AND used_index = 0 "
        "ORDER BY exec_time_ms DESC;"
    ),
    "l92": "EXPLAIN SELECT * FROM incidents WHERE district = 'Central';",
    "l93": "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_incidents_district';",
    "l94": "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_citizens_threat';",
    "l95": "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_incidents_severity_district';",
    "l96": (
        "SELECT c.name, c.district, i.type, i.severity, i.timestamp "
        "FROM incidents i "
        "JOIN citizens c ON i.citizen_id = c.id "
        "WHERE i.severity = 'CRITICAL' AND i.resolved = 0 AND c.threat_flag = 1 "
        "ORDER BY i.timestamp;"
    ),
    "l97": "SELECT query_text, exec_time_ms, used_index FROM query_log ORDER BY ran_at DESC LIMIT 2;",
}

LEVEL9_DDL = """
CREATE TABLE citizens (
    id INTEGER PRIMARY KEY,
    name TEXT,
    district TEXT,
    threat_flag INTEGER,
    last_seen TEXT
);

CREATE TABLE incidents (
    id INTEGER PRIMARY KEY,
    citizen_id INTEGER,
    type TEXT,
    district TEXT,
    severity TEXT,
    timestamp TEXT,
    resolved INTEGER,
    FOREIGN KEY (citizen_id) REFERENCES citizens(id)
);

CREATE TABLE query_log (
    id INTEGER PRIMARY KEY,
    query_text TEXT,
    exec_time_ms INTEGER,
    ran_at TEXT,
    used_index INTEGER
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
    2: {
        "ddl": LEVEL2_DDL,
        "tables": {
            "drones": LEVEL2_DATA["drones"],
            "receivers": LEVEL2_DATA["receivers"],
            "transmissions": LEVEL2_DATA["transmissions"],
        },
        "static_queries": LEVEL2_STATIC_QUERIES,
    },
    3: {
        "ddl": LEVEL3_DDL,
        "tables": {
            "suspects": LEVEL3_DATA["suspects"],
            "items_catalog": LEVEL3_DATA["items_catalog"],
            "transactions": LEVEL3_DATA["transactions"],
        },
        "static_queries": LEVEL3_STATIC_QUERIES,
    },
    4: {
        "ddl": LEVEL4_DDL,
        "tables": {
            "accounts": LEVEL4_DATA["accounts"],
            "bank_transactions": LEVEL4_DATA["bank_transactions"],
        },
        "static_queries": LEVEL4_STATIC_QUERIES,
    },
    5: {
        "ddl": LEVEL5_DDL,
        "tables": {
            "agents": LEVEL5_DATA["agents"],
            "orders": LEVEL5_DATA["orders"],
        },
        "static_queries": LEVEL5_STATIC_QUERIES,
    },
    6: {
        "ddl": LEVEL6_DDL,
        "tables": {
            "agents": LEVEL6_DATA["agents"],
            "memory_files": LEVEL6_DATA["memory_files"],
            "encryption_keys": LEVEL6_DATA["encryption_keys"],
            "archive_sessions": LEVEL6_DATA["archive_sessions"],
        },
        "static_queries": LEVEL6_STATIC_QUERIES,
    },
    7: {
        "ddl": LEVEL7_DDL,
        "tables": {
            "evidence": LEVEL7_DATA["evidence"],
            "witnesses": LEVEL7_DATA["witnesses"],
        },
        "static_queries": LEVEL7_STATIC_QUERIES,
        "check_queries": LEVEL7_CHECK_QUERIES,
    },
    8: {
        "ddl": LEVEL8_DDL,
        "tables": {
            "balances": LEVEL8_DATA["balances"],
            "ledger": LEVEL8_DATA["ledger"],
        },
        "static_queries": LEVEL8_STATIC_QUERIES,
        "check_queries": LEVEL8_CHECK_QUERIES,
    },
    9: {
        "ddl": LEVEL9_DDL,
        "tables": {
            "citizens": LEVEL9_DATA["citizens"],
            "incidents": LEVEL9_DATA["incidents"],
            "query_log": LEVEL9_DATA["query_log"],
        },
        "static_queries": LEVEL9_STATIC_QUERIES,
        "check_queries": LEVEL9_CHECK_QUERIES,
    },
}
