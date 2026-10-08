import os
import sqlite3

# Absolute path so the DB is always created next to your scripts
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quizverse.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables, then auto-load questions from questions.py if the table is empty."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            option1 TEXT, option2 TEXT, option3 TEXT, option4 TEXT,
            answer TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            score INTEGER,
            total INTEGER,
            attempted INTEGER,
            taken_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()

    # One-time automatic migration from questions.py
    count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    if count == 0:
        try:
            from questions import questions as old_questions
            for category, items in old_questions.items():
                for q in items:
                    o = q["options"]
                    conn.execute(
                        "INSERT INTO questions "
                        "(category, question, option1, option2, option3, option4, answer) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (category, q["question"], o[0], o[1], o[2], o[3], q["answer"]))
            conn.commit()
            print("Questions migrated from questions.py into the database.")
        except ImportError:
            print("questions.py not found - questions table is empty.")
    conn.close()


def get_or_create_user(name):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", (name,))
    conn.commit()
    row = conn.execute("SELECT id FROM users WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row[0]


def get_categories():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT category FROM questions").fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_questions(category):
    """Returns the same list-of-dicts format the app already uses."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT question, option1, option2, option3, option4, answer "
        "FROM questions WHERE category = ?", (category,)).fetchall()
    conn.close()
    return [{"question": r[0], "options": [r[1], r[2], r[3], r[4]], "answer": r[5]}
            for r in rows]


def save_result(name, category, score, total, attempted):
    user_id = get_or_create_user(name)
    conn = get_connection()
    conn.execute(
        "INSERT INTO results (user_id, category, score, total, attempted) "
        "VALUES (?, ?, ?, ?, ?)", (user_id, category, score, total, attempted))
    conn.commit()
    conn.close()


def get_leaderboard(category, limit=10):
    """Best score per player in a category: [(name, best_score, total, date), ...]"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT u.name, MAX(r.score) AS best, MAX(r.total), MAX(r.taken_at)
        FROM results r JOIN users u ON u.id = r.user_id
        WHERE r.category = ?
        GROUP BY u.id
        ORDER BY best DESC, MAX(r.taken_at) ASC
        LIMIT ?""", (category, limit)).fetchall()
    conn.close()
    return rows


def get_user_history(name, limit=10):
    """Latest attempts of a player: [(category, score, total, date), ...]"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.category, r.score, r.total, r.taken_at
        FROM results r JOIN users u ON u.id = r.user_id
        WHERE u.name = ?
        ORDER BY r.taken_at DESC, r.id DESC
        LIMIT ?""", (name, limit)).fetchall()
    conn.close()
    return rows