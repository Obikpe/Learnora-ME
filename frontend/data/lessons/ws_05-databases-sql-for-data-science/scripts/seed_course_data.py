"""Create a small, repeatable SQLite dataset used by WS05 lesson examples.

Run from the course folder:
    python scripts/seed_course_data.py

The script is safe to rerun: tables are created only when absent and sample
rows use INSERT OR IGNORE. It does not delete existing learner work.
"""
from pathlib import Path
import sqlite3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "learning.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    programme TEXT NOT NULL,
    age INTEGER,
    email TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS courses (
    course_id INTEGER PRIMARY KEY,
    course_title TEXT NOT NULL,
    duration_hours REAL
);

CREATE TABLE IF NOT EXISTS enrolments (
    enrolment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_on TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    UNIQUE(student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    region TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    region TEXT,
    order_date TEXT NOT NULL,
    amount REAL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS activities (
    activity_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    activity_date TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS monthly_revenue (
    month TEXT PRIMARY KEY,
    revenue REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS product_revenue (
    product TEXT PRIMARY KEY,
    revenue REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS current_students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS former_students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS cohort_a (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cohort_b (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scholarship_recipients (
    student_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS registered_students (
    student_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS completed_students (
    student_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    manager_id INTEGER,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY,
    balance REAL NOT NULL CHECK (balance >= 0)
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY,
    action TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    paid_on TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
"""

def seed(connection):
    connection.executescript(SCHEMA)

    connection.executemany(
        """INSERT OR IGNORE INTO students
           (student_id, name, programme, age, email)
           VALUES (?, ?, ?, ?, ?)""",
        [
            (1, "Ada", "Data Science", 22, "ada@example.test"),
            (2, "Musa", "Statistics", 25, "musa@example.test"),
            (3, "Tola", "Data Science", 21, "tola@example.test"),
            (4, "Kemi", "Business Analytics", 24, "kemi@example.test"),
        ],
    )
    connection.executemany(
        """INSERT OR IGNORE INTO courses
           (course_id, course_title, duration_hours)
           VALUES (?, ?, ?)""",
        [
            (1, "Python for Analysis", 12),
            (2, "SQL Foundations", 10),
            (3, "Statistics", 15),
            (4, "Data Visualisation", 8),
        ],
    )
    connection.executemany(
        """INSERT OR IGNORE INTO enrolments
           (enrolment_id, student_id, course_id, enrolled_on, status)
           VALUES (?, ?, ?, ?, ?)""",
        [
            (1, 1, 1, "2026-01-05", "completed"),
            (2, 1, 2, "2026-01-06", "completed"),
            (3, 2, 2, "2026-01-08", "active"),
            (4, 3, 1, "2026-01-10", "active"),
            (5, 4, 4, "2026-01-12", "completed"),
        ],
    )
    connection.executemany(
        """INSERT OR IGNORE INTO customers
           (customer_id, customer_name, region) VALUES (?, ?, ?)""",
        [
            (1, "Customer A", "North"),
            (2, "Customer B", "South"),
            (3, "Customer C", "East"),
            (4, "Customer D", "West"),
        ],
    )
    connection.executemany(
        """INSERT OR IGNORE INTO orders
           (order_id, customer_id, region, order_date, amount, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [
            (1, 1, "North", "2026-01-03", 45000, "completed"),
            (2, 1, "North", "2026-01-18", 65000, "completed"),
            (3, 2, "South", "2026-02-04", 82000, "completed"),
            (4, 2, "South", "2026-02-19", 25000, "cancelled"),
            (5, 3, "East", "2026-03-02", 120000, "completed"),
            (6, 3, "East", "2026-03-17", 55000, "completed"),
            (7, 4, "West", "2026-04-06", 30000, "completed"),
            (8, 4, "West", "2026-04-21", 90000, "completed"),
        ],
    )
    connection.executemany(
        """INSERT OR IGNORE INTO activities
           (activity_id, customer_id, activity_date) VALUES (?, ?, ?)""",
        [
            (1, 1, "2026-01-03"), (2, 1, "2026-02-01"),
            (3, 2, "2026-02-04"), (4, 3, "2026-03-02"),
            (5, 3, "2026-04-02"), (6, 4, "2026-04-06"),
        ],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO monthly_revenue (month, revenue) VALUES (?, ?)",
        [
            ("2026-01", 110000), ("2026-02", 107000),
            ("2026-03", 175000), ("2026-04", 120000),
        ],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO product_revenue (product, revenue) VALUES (?, ?)",
        [
            ("Laptop", 450000), ("Phone", 620000),
            ("Headphones", 180000), ("Tablet", 260000),
        ],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO current_students VALUES (?, ?, ?)",
        [(1, "Ada", "ada@example.test"), (2, "Musa", "musa@example.test")],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO former_students VALUES (?, ?, ?)",
        [(3, "Tola", "tola@example.test"), (4, "Kemi", "kemi@example.test")],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO cohort_a VALUES (?, ?)",
        [(1, "Ada"), (2, "Musa"), (3, "Tola")],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO cohort_b VALUES (?, ?)",
        [(2, "Musa"), (3, "Tola"), (4, "Kemi")],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO scholarship_recipients VALUES (?)",
        [(1,), (3,)],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO registered_students VALUES (?)",
        [(1,), (2,), (3,), (4,)],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO completed_students VALUES (?)",
        [(1,), (3,)],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO employees VALUES (?, ?, ?)",
        [(1, "Manager", None), (2, "Analyst", 1), (3, "Associate", 1)],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO accounts VALUES (?, ?)",
        [(1, 50000), (2, 30000)],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO payments (payment_id, student_id, amount, paid_on) VALUES (?, ?, ?, ?)",
        [(1, 1, 25000, "2026-01-10"), (2, 2, 18000, "2026-01-12")],
    )

def main():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        seed(connection)
    print(f"Course database is ready: {DB_PATH}")

if __name__ == "__main__":
    main()
