"""Smoke test for smart_billing_app: DatabaseManager CRUD on a temp database."""
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager


def main():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        db = DatabaseManager(db_path=path)
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)",
            ("Smoke Widget", 99.5, "test", 10),
        )
        conn.commit()
        cur.execute("SELECT name, price FROM products WHERE name=?", ("Smoke Widget",))
        row = cur.fetchone()
        assert row == ("Smoke Widget", 99.5), row
        conn.close()
    finally:
        os.unlink(path)

    print("smoke OK: DatabaseManager init + product insert/select")


if __name__ == "__main__":
    main()
