# Smart Billing App

**Desktop GUI app (tkinter)** — offline billing/invoicing app with local SQLite database. Product management, billing screen, reports, analytics, printing/export.

## Run

```bash
python main.py          # launches the desktop GUI window
```

Needs a display (works under `xvfb-run` on headless Linux).

## Deps

Standard library + tkinter only. Boot verified under `xvfb-run` on Python 3.12: database initializes, main window opens, no traceback.

## Notes

- Data is stored in a local SQLite file created next to the app (`startup_debug.txt` logs each boot).
- Not a web/cloud app — runs as a local desktop window.
