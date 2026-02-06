import sqlite3
import datetime
import calendar
from database import DatabaseManager

class AnalyticsManager:
    def __init__(self):
        self.db = DatabaseManager()

    def get_todays_earnings(self):
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        conn = self.db.get_connection()
        cursor = conn.cursor()
        # Note: date column in bills is 'YYYY-MM-DD HH:MM:SS'
        cursor.execute("SELECT SUM(total_amount) FROM bills WHERE date LIKE ?", (f"{today_str}%",))
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0.0

    def get_monthly_earnings(self):
        now = datetime.datetime.now()
        month_str = now.strftime("%Y-%m")
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total_amount) FROM bills WHERE date LIKE ?", (f"{month_str}%",))
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0.0
        
    def get_yearly_earnings(self):
        year_str = datetime.datetime.now().strftime("%Y")
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total_amount) FROM bills WHERE date LIKE ?", (f"{year_str}%",))
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0.0

    def get_top_products(self, limit=5):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT product_name, COUNT(DISTINCT bill_id) as freq, SUM(total) as revenue 
            FROM bill_items 
            GROUP BY product_name 
            ORDER BY freq DESC 
            LIMIT ?
        ''', (limit,))
        data = cursor.fetchall() #(name, qty, revenue)
        conn.close()
        return data

    def get_low_products(self, limit=5):
        # Simplistic approach: Items with least quantity sold
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT product_name, COUNT(DISTINCT bill_id) as freq, SUM(total) as revenue 
            FROM bill_items 
            GROUP BY product_name 
            ORDER BY freq ASC 
            LIMIT ?
        ''', (limit,))
        data = cursor.fetchall()
        conn.close()
        return data
        
    def get_last_7_days_revenue(self):
        # Returns list of (date_label, amount)
        data = {}
        for i in range(6, -1, -1):
            day = datetime.datetime.now() - datetime.timedelta(days=i)
            key = day.strftime("%Y-%m-%d")
            data[key] = 0.0
            
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get data for range
        start_date = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
        cursor.execute("SELECT date, total_amount FROM bills WHERE date >= ?", (start_date,))
        rows = cursor.fetchall()
        conn.close()
        
        for r_date, amount in rows:
            # r_date is YYYY-MM-DD HH:MM:SS
            day_key = r_date.split(" ")[0]
            if day_key in data:
                data[day_key] += amount
                
        return list(data.keys()), list(data.values())
