import os

import sys

DB_NAME = "billing.db"

if getattr(sys, 'frozen', False):
    # If run as EXE, use the executable's directory
    APP_DIR = os.path.dirname(sys.executable)
else:
    # If run as script, use the script's directory
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(APP_DIR, DB_NAME)

# Default Settings
DEFAULT_GST_PERCENT = 18.0
CURRENCY_SYMBOL = "₹"
