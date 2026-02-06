import os
import subprocess
import sys

def build_debug():
    # Define build command - NO --windowed here to verify errors
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        # "--windowed",  <-- COMMENTED OUT FOR DEBUGGING
        "--name", "SmartBillingPro_Debug",
        "--clean",
        "--hidden-import", "tkinter",
        "--hidden-import", "sqlite3",
        "main.py"
    ]
    
    # Check for icon
    if os.path.exists("app.ico"):
        cmd.extend(["--icon", "app.ico"])
        
    print(f"Running DEBUG build command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\nDEBUG Build Complete! Check 'dist/SmartBillingPro_Debug.exe'")

if __name__ == "__main__":
    build_debug()
