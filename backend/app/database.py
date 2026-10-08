import os
import sqlite3
from pathlib import Path
from typing import Generator

# Base database path in backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "campus_connect.db"


def get_db_path() -> str:
    """Return the absolute path to the SQLite database file."""
    return str(DB_FILE)


def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a new SQLite database connection configured with:
    - Row factory enabled for column name access like dictionaries.
    - Foreign keys enforced.
    - Write-Ahead Logging (WAL) for concurrency.
    """
    conn = sqlite3.connect(get_db_path(), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    FastAPI dependency that yields a database connection
    and guarantees it is closed after request handling.
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """
    Initialize SQLite database tables and seed default demo data if empty.
    Runs automatically on FastAPI application startup.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Users Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                department TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Issues Table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL CHECK(category IN ('Classroom', 'Campus', 'Lost & Found', 'General')),
                status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open', 'In Progress', 'Resolved')),
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
            """
        )

        # Indexes for fast filtering
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_issues_status ON issues (status);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_issues_category ON issues (category);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_issues_user_id ON issues (user_id);"
        )

        conn.commit()

        # Check if users table is empty; if so, seed demo account and sample issues
        cursor.execute("SELECT COUNT(*) AS count FROM users;")
        user_count = cursor.fetchone()["count"]

        if user_count == 0:
            # Import here to prevent circular imports
            from app.auth import hash_password

            demo_password = hash_password("password123")
            cursor.execute(
                """
                INSERT INTO users (full_name, email, password_hash, department)
                VALUES (?, ?, ?, ?);
                """,
                (
                    "Aarav Sharma",
                    "aarav.sharma@campus.edu",
                    demo_password,
                    "Computer Science & Engineering - 3rd Year",
                ),
            )
            demo_user_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO users (full_name, email, password_hash, department)
                VALUES (?, ?, ?, ?);
                """,
                (
                    "Priya Patel",
                    "priya.patel@campus.edu",
                    demo_password,
                    "Electronics & Communication - 2nd Year",
                ),
            )
            priya_user_id = cursor.lastrowid

            # Seed realistic issues across all required categories
            sample_issues = [
                (
                    "Projector bulb flickering in Room 302 (CS Block)",
                    "The overhead projector in Room 302 flickers continuously and turns off every 10 minutes during lectures. Needs bulb replacement or cable inspection.",
                    "Classroom",
                    "Open",
                    demo_user_id,
                ),
                (
                    "Water cooler on 2nd Floor Library leaking water",
                    "The drinking water dispenser outside the central library reading hall is leaking from the drainage valve, creating a slippery puddle.",
                    "Campus",
                    "In Progress",
                    priya_user_id,
                ),
                (
                    "Found Blue Hydro Flask Water Bottle in Cafeteria",
                    "Found a metallic blue Hydro Flask bottle with an anime sticker on table #4 near the cafeteria counter around 1:30 PM today. Kept with the cafeteria supervisor.",
                    "Lost & Found",
                    "Open",
                    demo_user_id,
                ),
                (
                    "Wi-Fi disconnects repeatedly in Study Hall B",
                    "Students are unable to maintain an active connection on the 'Campus-Student' Wi-Fi network near the north wing of Study Hall B.",
                    "Campus",
                    "Resolved",
                    priya_user_id,
                ),
                (
                    "Digital Library terminal 07 keyboard keys sticking",
                    "Keys 'E' and 'Space' on desktop #07 in the digital reference section are stuck and difficult to press.",
                    "General",
                    "Open",
                    demo_user_id,
                ),
            ]

            cursor.executemany(
                """
                INSERT INTO issues (title, description, category, status, user_id)
                VALUES (?, ?, ?, ?, ?);
                """,
                sample_issues,
            )
            conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Database initialization failed: {e}") from e
    finally:
        conn.close()
