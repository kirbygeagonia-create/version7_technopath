"""
Gunicorn configuration for Render deployment.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault('SERVER_SOFTWARE', 'gunicorn')

BASE_DIR = Path(__file__).resolve().parent
_migrations_done = False


def on_starting(server):
    """Attempt migrations with retry — internal DB hostname may need a moment."""
    global _migrations_done
    manage = str(BASE_DIR / "manage.py")

    # Retry for up to 60 seconds waiting for the internal DB to resolve
    for attempt in range(12):
        print(f"[gunicorn] migrate attempt {attempt + 1}/12...", flush=True)
        result = subprocess.run(
            [sys.executable, manage, "migrate", "--no-input"],
            capture_output=False,
        )
        if result.returncode == 0:
            print("[gunicorn] Migrations complete.", flush=True)
            _migrations_done = True
            # Run seed after successful migrate
            subprocess.run(
                [sys.executable, manage, "seed_bulk_campus"],
                capture_output=False,
            )
            print("[gunicorn] Seed complete.", flush=True)
            return
        print(f"[gunicorn] migrate failed, retrying in 5s...", flush=True)
        time.sleep(5)

    print("[gunicorn] migrate never succeeded — workers will start anyway.", flush=True)


workers = 2
timeout = 120
