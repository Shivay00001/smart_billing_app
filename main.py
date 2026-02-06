import os
import sys
import datetime
import traceback

# DEBUG: Root Logging
LOG_FILE = "startup_debug.txt"
def log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

# Clear old log
if os.path.exists(LOG_FILE): os.remove(LOG_FILE)

log("--- Starting Application ---")
log(f"Executable: {sys.executable}")
log(f"CWD: {os.getcwd()}")

try:
    log("Importing tkinter...")
    import tkinter as tk
    from tkinter import ttk, messagebox
    log("Tkinter imported.")
    
    log("Importing database...")
    from database import DatabaseManager
    log("Database imported.")
    
    log("Importing UI...")
    from ui.main_window import MainWindow
    log("UI imported.")
except Exception as e:
    log(f"CRITICAL IMPORT ERROR:\n{traceback.format_exc()}")
    # Fallback to absolute basic error display
    try:
        import tkinter
        r = tkinter.Tk()
        r.withdraw()
        from tkinter import messagebox
        messagebox.showerror("Startup Error", f"Failed to load dependencies.\n\n{str(e)}\n\nCheck startup_debug.txt")
    except:
        pass
    sys.exit(1)

def main():
    log("Entering main()...")
    try:
        log("Initializing DatabaseManager...")
        db = DatabaseManager()
        log("Database ready.")
        
        log("Creating MainWindow...")
        app = MainWindow()
        log("MainWindow created. Starting mainloop.")
        app.mainloop()
        log("Mainloop exited normally.")
    except Exception as e:
        error_msg = traceback.format_exc()
        log(f"RUNTIME ERROR:\n{error_msg}")
        try:
            messagebox.showerror("Application Error", f"The application crashed.\n\n{str(e)}\n\nSee startup_debug.txt for details.")
        except:
            pass

if __name__ == "__main__":
    main()
