import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import sqlite3
from database import DatabaseManager
from config import DEFAULT_GST_PERCENT
from core.printing import PrintManager

class BillingScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.db = DatabaseManager()
        self.cart_items = []  # List of dicts: {name, qty, price, total}
        
        self._init_ui()

    def _init_ui(self):
        # Top Section: Customer Info & Bill Meta
        top_frame = ttk.Frame(self, style="Card.TFrame", padding=15)
        top_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(top_frame, text="Customer Name").grid(row=0, column=0, sticky="w", padx=5)
        self.entry_cust_name = ttk.Entry(top_frame, width=30)
        self.entry_cust_name.grid(row=0, column=1, padx=5)

        ttk.Label(top_frame, text="Phone No.").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_cust_phone = ttk.Entry(top_frame, width=20)
        self.entry_cust_phone.grid(row=0, column=3, padx=5)

        ttk.Label(top_frame, text="Payment Mode").grid(row=0, column=4, sticky="w", padx=5)
        self.combo_payment = ttk.Combobox(top_frame, values=["Cash", "UPI", "Card"], state="readonly", width=10)
        self.combo_payment.current(0)
        self.combo_payment.grid(row=0, column=5, padx=5)

        # GST Toggle
        self.var_gst = tk.BooleanVar(value=True)
        self.chk_gst = ttk.Checkbutton(top_frame, text="Enable GST", variable=self.var_gst, command=self._recalculate_totals)
        self.chk_gst.grid(row=0, column=6, padx=15)
        
        # Stock Status
        self.lbl_stock_status = ttk.Label(top_frame, text="", font=("Segoe UI", 10, "bold"))
        self.lbl_stock_status.grid(row=0, column=7, padx=15)

        # Middle Section: Product Entry
        entry_frame = ttk.Frame(self, style="Card.TFrame", padding=15)
        entry_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(entry_frame, text="Product Name").grid(row=0, column=0, sticky="w", padx=5)
        self.entry_product = ttk.Entry(entry_frame, width=40)
        self.entry_product.grid(row=1, column=0, padx=5)
        self.entry_product.bind("<KeyRelease>", self._on_product_type) # For autocomplete logic later

        ttk.Label(entry_frame, text="Price").grid(row=0, column=1, sticky="w", padx=5)
        self.entry_price = ttk.Entry(entry_frame, width=15)
        self.entry_price.grid(row=1, column=1, padx=5)

        ttk.Label(entry_frame, text="Qty").grid(row=0, column=2, sticky="w", padx=5)
        self.entry_qty = ttk.Entry(entry_frame, width=10)
        self.entry_qty.insert(0, "1")
        self.entry_qty.grid(row=1, column=2, padx=5)

        self.btn_add = ttk.Button(entry_frame, text="Add Item", style="Primary.TButton", command=self._add_item)
        self.btn_add.grid(row=1, column=3, padx=15)

        # Main Section: Cart Table
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill="both", expand=True)

        cols = ("Name", "Price", "Qty", "Total")
        self.tree = ttk.Treeview(self.tree_frame, columns=cols, show="headings", height=12)
        
        self.tree.column("Name", width=400)
        self.tree.column("Price", width=100, anchor="e")
        self.tree.column("Qty", width=80, anchor="center")
        self.tree.column("Total", width=100, anchor="e")

        for col in cols:
            self.tree.heading(col, text=col)

        self.tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Bottom Section: Totals & Actions
        bottom_frame = ttk.Frame(self, style="Card.TFrame", padding=20)
        bottom_frame.pack(fill="x", pady=10)

        # Totals Display
        self.lbl_subtotal = ttk.Label(bottom_frame, text="Subtotal: ₹0.00", font=("Segoe UI", 12))
        self.lbl_subtotal.pack(side="top", anchor="e")
        
        self.lbl_tax = ttk.Label(bottom_frame, text="GST (18%): ₹0.00", font=("Segoe UI", 12))
        self.lbl_tax.pack(side="top", anchor="e")
        
        self.lbl_grand_total = ttk.Label(bottom_frame, text="Total: ₹0.00", font=("Segoe UI", 18, "bold"), foreground="#005f73")
        self.lbl_grand_total.pack(side="top", anchor="e", pady=5)

        # Action Buttons
        btn_print = ttk.Button(bottom_frame, text="Save & Print", style="Accent.TButton", command=self._save_bill)
        btn_print.pack(side="right", padx=5)
        
        btn_clear = ttk.Button(bottom_frame, text="Clear", command=self._clear_all)
        btn_clear.pack(side="right", padx=5)

    def _on_product_type(self, event):
        # Basic "Intelligence" - Check if product exists in DB and autofill price
        # This is a simple implementation. Ideally we'd show a dropdown.
        name = self.entry_product.get().strip()
        if len(name) < 3: return
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT price, stock_quantity FROM products WHERE name LIKE ? LIMIT 1", (name,))
        res = cursor.fetchone()
        conn.close()
        
        if res:
            price, stock = res
            current_price = self.entry_price.get()
            if not current_price: # Only autocomplete if empty to avoid annoying user
                self.entry_price.delete(0, tk.END)
                self.entry_price.insert(0, str(price))
                
            # Update Stock Status
            if stock > 0:
                self.lbl_stock_status.config(text=f"Available: {stock}", foreground="green")
            else:
                self.lbl_stock_status.config(text=f"Available: {stock}", foreground="red")
        else:
             self.lbl_stock_status.config(text="New Product", foreground="blue")

    def _add_item(self):
        name = self.entry_product.get().strip()
        price = self.entry_price.get().strip()
        qty = self.entry_qty.get().strip()

        if not name or not price or not qty:
            messagebox.showerror("Error", "Please fill all item fields")
            return

        try:
            price = float(price)
            qty = int(qty)
            total = price * qty
        except ValueError:
            messagebox.showerror("Error", "Invalid Price or Qty")
            return

        # Add to cart list
        item = {"name": name, "price": price, "qty": qty, "total": total}
        self.cart_items.append(item)
        
        # Add to Treeview
        self.tree.insert("", "end", values=(name, f"₹{price:.2f}", qty, f"₹{total:.2f}"))
        
        # Update Totals
        self._recalculate_totals()
        
        # Clear entry fields for next item
        self.entry_product.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_qty.delete(0, tk.END)
        self.entry_qty.insert(0, "1")
        self.entry_product.focus()

    def _recalculate_totals(self):
        subtotal = sum(item["total"] for item in self.cart_items)
        
        gst_amount = 0
        if self.var_gst.get():
            gst_amount = subtotal * (DEFAULT_GST_PERCENT / 100)
            self.lbl_tax.config(text=f"GST ({DEFAULT_GST_PERCENT}%): ₹{gst_amount:.2f}")
            self.lbl_tax.pack(side="top", anchor="e") # Ensure visible
        else:
            self.lbl_tax.pack_forget() # Hide if no GST

        grand_total = subtotal + gst_amount
        
        self.lbl_subtotal.config(text=f"Subtotal: ₹{subtotal:.2f}")
        self.lbl_grand_total.config(text=f"Total: ₹{grand_total:.2f}")

    def _save_bill(self):
        if not self.cart_items:
            messagebox.showwarning("Empty", "Cart is empty")
            return
            
        cust_name = self.entry_cust_name.get().strip() or "Walk-in"
        cust_phone = self.entry_cust_phone.get().strip()
        pay_mode = self.combo_payment.get()
        
        # Calculate final numbers
        subtotal = sum(item["total"] for item in self.cart_items)
        tax = subtotal * (DEFAULT_GST_PERCENT / 100) if self.var_gst.get() else 0
        total = subtotal + tax
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bill_no = f"INV-{int(datetime.datetime.now().timestamp())}" # Simple ID

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Save Bill
            cursor.execute('''
                INSERT INTO bills (bill_number, date, customer_name, customer_phone, total_amount, tax_amount, payment_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (bill_no, date_str, cust_name, cust_phone, total, tax, pay_mode))
            
            bill_id = cursor.lastrowid
            
            # Save Items & Updates Products (Intelligence)
            for item in self.cart_items:
                cursor.execute('''
                    INSERT INTO bill_items (bill_id, product_name, qty, price, total)
                    VALUES (?, ?, ?, ?, ?)
                ''', (bill_id, item['name'], item['qty'], item['price'], item['total']))
                
                # Update/Insert Product Intelligence
                # Check if exists
                cursor.execute("SELECT id FROM products WHERE name = ?", (item['name'],))
                existing = cursor.fetchone()
                if not existing:
                    # New product found in billing, add to DB with 0 initial stock (will go negative if we subtract?)
                    # Alternatively, just track it. Let's add it.
                    cursor.execute("INSERT INTO products (name, price, stock_quantity) VALUES (?, ?, ?)", (item['name'], item['price'], 0 - item['qty']))
                else:
                    # Update stock
                    cursor.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?", (item['qty'], existing[0]))

            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Bill Saved! ID: {bill_no}")
            self._print_bill(bill_id) # Placeholder
            self._clear_all()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {e}")

    def _print_bill(self, bill_id):
        pm = PrintManager()
        pm.generate_and_preview(bill_id)

    def _clear_all(self):
        self.cart_items = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.entry_cust_name.delete(0, tk.END)
        self.entry_cust_phone.delete(0, tk.END)
        self._recalculate_totals()
