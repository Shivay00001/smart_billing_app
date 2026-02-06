import sqlite3
import os
from config import DB_PATH

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize the database with required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Products Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                category TEXT,
                stock_quantity INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_name ON products(name)')
        
        # Migration: Add stock_quantity if it doesn't exist (for existing DBs)
        try:
            cursor.execute("SELECT stock_quantity FROM products LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE products ADD COLUMN stock_quantity INTEGER DEFAULT 0")

        # Bills Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_number TEXT NOT NULL UNIQUE,
                date TEXT NOT NULL,
                customer_name TEXT,
                customer_phone TEXT,
                total_amount REAL NOT NULL,
                tax_amount REAL DEFAULT 0,
                payment_mode TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bill_date ON bills(date)')

        # Bill Items Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                qty INTEGER NOT NULL,
                price REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
            )
        ''')

        # Settings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Exports Log Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exports_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                export_date TEXT NOT NULL,
                file_path TEXT
            )
        ''')

        conn.commit()
        conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    print(f"Database initialized at {db.db_path}")
