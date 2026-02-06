import csv
import datetime
import os
import sqlite3
from database import DatabaseManager

class Exporter:
    def __init__(self):
        self.db = DatabaseManager()
        self.export_dir = os.path.join(os.getcwd(), "exports")
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

    def export_weekly_data(self):
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=7)
        return self._export_range(start_date, end_date, "Weekly")

    def export_monthly_data(self):
        end_date = datetime.datetime.now()
        start_date = end_date.replace(day=1) # Start of current month
        return self._export_range(start_date, end_date, "Monthly")

    def _export_range(self, start_date, end_date, label):
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # specific query to join bills and items for a complete report
        query = f'''
            SELECT 
                b.bill_number, b.date, b.customer_name, b.customer_phone, 
                b.total_amount, b.tax_amount, b.payment_mode,
                bi.product_name, bi.qty, bi.price, bi.total as item_total
            FROM bills b
            JOIN bill_items bi ON b.bill_id = bi.bill_id
            WHERE b.date >= ? AND b.date <= ?
        '''
        
        try:
            cursor.execute(query, (start_str, f"{end_str} 23:59:59"))
            rows = cursor.fetchall()
            
            if not rows:
                return False, "No data found for this period"
            
            # Column headers
            headers = [description[0] for description in cursor.description]
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{label}_Report_{timestamp}.csv"
            filepath = os.path.join(self.export_dir, filename)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            
            # Log export
            cursor.execute("INSERT INTO exports_log (export_date, file_path) VALUES (?, ?)", 
                           (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), filepath))
            conn.commit()
            
            return True, filepath
            
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
