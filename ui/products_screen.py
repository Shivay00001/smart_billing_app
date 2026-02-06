import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DatabaseManager
from ui.styles import ThemeManager

class ProductsScreen(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Main.TFrame")
        self.db = DatabaseManager()
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        # Header
        header_frame = ttk.Frame(self, style="Main.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(header_frame, text="Product Inventory", style="Header.TLabel").pack(side="left")

        # Search Bar
        search_frame = ttk.Frame(header_frame, style="Main.TFrame")
        search_frame.pack(side="right")
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.entry_search = ttk.Entry(search_frame)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", self._search_products)

        # Content Split: Left (Form) - Right (List)
        content_frame = ttk.Frame(self, style="Main.TFrame")
        content_frame.pack(fill="both", expand=True)

        # Left: Add/Edit Form
        form_frame = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        form_frame.pack(side="left", fill="y", padx=(0, 10))
        
        ttk.Label(form_frame, text="Product Details", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 15))

        self.var_id = tk.StringVar() # Hidden ID for updates

        ttk.Label(form_frame, text="Name").pack(anchor="w")
        self.entry_name = ttk.Entry(form_frame, width=30)
        self.entry_name.pack(anchor="w", pady=(0, 10))

        ttk.Label(form_frame, text="Category").pack(anchor="w")
        self.entry_cat = ttk.Entry(form_frame, width=30)
        self.entry_cat.pack(anchor="w", pady=(0, 10))
        
        ttk.Label(form_frame, text="Price (₹)").pack(anchor="w")
        self.entry_price = ttk.Entry(form_frame, width=30)
        self.entry_price.pack(anchor="w", pady=(0, 10))

        ttk.Label(form_frame, text="Stock Quantity").pack(anchor="w")
        self.entry_stock = ttk.Entry(form_frame, width=30)
        self.entry_stock.pack(anchor="w", pady=(0, 10))

        btn_frame = ttk.Frame(form_frame, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=20)
        
        self.btn_save = ttk.Button(btn_frame, text="Save Product", style="Primary.TButton", command=self._save_product)
        self.btn_save.pack(fill="x", pady=5)
        
        self.btn_clear = ttk.Button(btn_frame, text="Clear Form", command=self._clear_form)
        self.btn_clear.pack(fill="x", pady=5)
        
        self.btn_delete = ttk.Button(btn_frame, text="Delete Product", command=self._delete_product)
        self.btn_delete.pack(fill="x", pady=5)
        self.btn_delete.state(["disabled"]) # Initially disabled

        # Right: Product List
        list_frame = ttk.Frame(content_frame, style="Card.TFrame", padding=10)
        list_frame.pack(side="right", fill="both", expand=True)

        cols = ("ID", "Name", "Category", "Price", "Stock", "Sold")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=180)
        self.tree.column("Category", width=100)
        self.tree.column("Price", width=80, anchor="e")
        self.tree.column("Stock", width=80, anchor="center")
        self.tree.column("Sold", width=80, anchor="center")

        for col in cols:
            self.tree.heading(col, text=col)

        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load_data(self, search_query=""):
        # Clear current
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if search_query:
            q = f"%{search_query}%"
            # Left Join to get total sold
            cursor.execute("""
                SELECT p.id, p.name, p.category, p.price, p.stock_quantity, COALESCE(SUM(bi.qty), 0) 
                FROM products p 
                LEFT JOIN bill_items bi ON p.name = bi.product_name 
                WHERE p.name LIKE ? 
                GROUP BY p.id
                ORDER BY p.name
            """, (q,))
        else:
            cursor.execute("""
                SELECT p.id, p.name, p.category, p.price, p.stock_quantity, COALESCE(SUM(bi.qty), 0) 
                FROM products p 
                LEFT JOIN bill_items bi ON p.name = bi.product_name 
                GROUP BY p.id
                ORDER BY p.name
            """)
            
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            # row: id, name, cat, price, stock, sold
            self.tree.insert("", "end", values=(row[0], row[1], row[2], f"₹{row[3]:.2f}", row[4], row[5]))

    def _search_products(self, event):
        query = self.entry_search.get().strip()
        self._load_data(query)

    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        vals = item['values']
        
        # Populate form
        self.var_id.set(vals[0])
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, vals[1])
        
        self.entry_cat.delete(0, tk.END)
        if vals[2] != "None":
            self.entry_cat.insert(0, vals[2])
        
        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, str(vals[3]).replace("₹", ""))
        
        self.entry_stock.delete(0, tk.END)
        self.entry_stock.insert(0, vals[4])
        
        self.btn_save.config(text="Update Product")
        self.btn_delete.state(["!disabled"])

    def _save_product(self):
        name = self.entry_name.get().strip()
        cat = self.entry_cat.get().strip()
        price = self.entry_price.get().strip()
        stock = self.entry_stock.get().strip()
        
        if not name or not price:
            messagebox.showerror("Error", "Name and Price are required")
            return
            
        try:
            price = float(price)
            stock = int(stock) if stock else 0
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values for Price or Stock")
            return
            
        prod_id = self.var_id.get()
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if prod_id: # Update
                cursor.execute("""
                    UPDATE products 
                    SET name=?, category=?, price=?, stock_quantity=?
                    WHERE id=?
                """, (name, cat, price, stock, prod_id))
            else: # Insert
                cursor.execute("""
                    INSERT INTO products (name, category, price, stock_quantity)
                    VALUES (?, ?, ?, ?)
                """, (name, cat, price, stock))
                
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Product Saved Successfully")
            self._clear_form()
            self._load_data()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Product with this name already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Database Error: {e}")

    def _delete_product(self):
        prod_id = self.var_id.get()
        if not prod_id: return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            return
            
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (prod_id,))
            conn.commit()
            conn.close()
            
            self._clear_form()
            self._load_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

    def _clear_form(self):
        self.var_id.set("")
        self.entry_name.delete(0, tk.END)
        self.entry_cat.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)
        
        self.btn_save.config(text="Save Product")
        self.btn_delete.state(["disabled"])
        self.tree.selection_remove(self.tree.selection())
