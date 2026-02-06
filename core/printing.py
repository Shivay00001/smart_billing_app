import os
import webbrowser
import tempfile
from datetime import datetime
from database import DatabaseManager

class PrintManager:
    def __init__(self):
        self.db = DatabaseManager()

    def generate_and_preview(self, bill_id):
        bill_data = self._fetch_bill_details(bill_id)
        if not bill_data:
            return False, "Bill not found"
            
        html_content = self._generate_html(bill_data)
        
        # Save to temp file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"receipt_{bill_id}.html")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Open in default browser/viewer
        webbrowser.open(f"file://{file_path}")
        return True, "Opened in browser for printing"

    def _fetch_bill_details(self, bill_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get Bill Info
        cursor.execute("SELECT * FROM bills WHERE bill_id = ?", (bill_id,))
        bill_row = cursor.fetchone() # (id, number, date, cust, phone, total, tax, mode)
        if not bill_row:
            conn.close()
            return None
            
        # Get Items
        cursor.execute("SELECT product_name, qty, price, total FROM bill_items WHERE bill_id = ?", (bill_id,))
        items = cursor.fetchall()
        
        # Get Business Info
        cursor.execute("SELECT value FROM settings WHERE key='biz_name'")
        biz_name = cursor.fetchone()
        biz_name = biz_name[0] if biz_name else "My Business"
        
        cursor.execute("SELECT value FROM settings WHERE key='company_logo'")
        logo_path = cursor.fetchone()
        logo_path = logo_path[0] if logo_path else None
        
        cursor.execute("SELECT value FROM settings WHERE key='print_format'")
        p_fmt = cursor.fetchone()
        p_fmt = p_fmt[0] if p_fmt else "Thermal 80mm"
        
        conn.close()
        
        return {
            "bill": bill_row,
            "items": items,
            "biz_name": biz_name,
            "logo_path": logo_path,
            "print_format": p_fmt
        }

    def _generate_html(self, data):
        bill = data["bill"]
        items = data["items"]
        biz_name = data["biz_name"]
        logo_path = data.get("logo_path")
        p_fmt = data.get("print_format", "Thermal 80mm")
        
        # Dynamic CSS Config
        if p_fmt == "Thermal 58mm":
            body_width = "180px"
            font_size = "10px"
            margin = "5px"
        elif p_fmt == "A4 (Standard)":
            body_width = "90%" # Responsive for A4
            font_size = "14px"
            margin = "20px"
        else: # 80mm Default
            body_width = "300px"
            font_size = "12px"
            margin = "10px"

        # bill: id, number, date, cust, phone, total, tax, mode
        bill_no = bill[1]
        date = bill[2]
        cust_name = bill[3]
        total = bill[5]
        tax = bill[6]
        
        logo_html = ""
        if logo_path and os.path.exists(logo_path):
            logo_html = f'<img src="file:///{logo_path.replace(os.sep, "/")}" style="max-width: 80%; max-height: 80px; display: block; margin: 0 auto 10px auto;">'
        
        rows_html = ""
        for name, qty, price, item_total in items:
            rows_html += f"""
            <tr>
                <td>{name}</td>
                <td style="text-align:center">{qty}</td>
                <td style="text-align:right">{price:.2f}</td>
                <td style="text-align:right">{item_total:.2f}</td>
            </tr>
            """
            
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Courier New', monospace; width: {body_width}; margin: 0 auto; padding: {margin}; font-size: {font_size}; }}
                .header {{ text-align: center; border-bottom: 2px dashed #000; padding-bottom: 10px; margin-bottom: 10px; }}
                .meta {{ margin-bottom: 10px; }}
                table {{ width: 100%; font-size: inherit; border-collapse: collapse; }}
                th {{ text-align: left; border-bottom: 1px solid #000; }}
                .totals {{ margin-top: 10px; border-top: 1px dashed #000; padding-top: 5px; text-align: right; }}
                .footer {{ margin-top: 20px; text-align: center; font-size: 0.9em; }}
                
                @media print {{
                    @page {{ margin: 0; }}
                    body {{ width: 100%; margin: 0; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                {logo_html}
                <h2>{biz_name}</h2>
                <p>Receipt / Tax Invoice</p>
            </div>
            
            <div class="meta">
                Bill No: {bill_no}<br>
                Date: {date}<br>
                Customer: {cust_name}<br>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Item</th>
                        <th style="text-align:center">Qty</th>
                        <th style="text-align:right">Price</th>
                        <th style="text-align:right">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            
            <div class="totals">
                <p>Tax: {tax:.2f}</p>
                <h3>Total: {total:.2f}</h3>
            </div>
            
            <div class="footer">
                Thank you for your business!
            </div>
            
            <script>
                window.print();
            </script>
        </body>
        </html>
        """
        return html
