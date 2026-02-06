import os
import subprocess
import sys

def build():
    # Define build command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",       # Switch to directory for better reliability/debugging
        "--windowed",
        "--name", "SmartBillingPro",
        "--clean",
        "--exclude-module", "torch",
        "--exclude-module", "scipy",
        "--exclude-module", "cv2",
        "--exclude-module", "tensorflow",
        "--exclude-module", "pandas",
        "--exclude-module", "openpyxl",
        "--hidden-import", "tkinter",
        "--hidden-import", "sqlite3",
        "main.py"
    ]
    
    # Check for icon
    if os.path.exists("app_icon.png"):
        try:
            from PIL import Image
            img = Image.open("app_icon.png")
            img.save("app.ico")
            print("Converted app_icon.png to app.ico")
            cmd.extend(["--icon", "app.ico"])
        except ImportError:
            print("Pillow not installed, skipping icon conversion. pip install pillow")
        except Exception as e:
            print(f"Icon conversion failed: {e}")
            
    print(f"Running build command: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\nBuild Complete! Check 'dist/' folder.")

if __name__ == "__main__":
    # Ensure dependencies
    print("Please ensure pyinstaller is installed: pip install pyinstaller")
    build()
