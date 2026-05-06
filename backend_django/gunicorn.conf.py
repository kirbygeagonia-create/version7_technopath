"""
Gunicorn configuration for Render deployment.
Runs Django migrations before workers start (on_starting hook),
so the port binds immediately while DB setup happens in the master process.
"""
import os
import subprocess
import sys
from pathlib import Path

# Set a marker so apps.py ready() hooks know we're in gunicorn runtime
os.environ.setdefault('SERVER_SOFTWARE', 'gunicorn')

# Resolve manage.py path relative to this config file
BASE_DIR = Path(__file__).resolve().parent


def on_starting(server):
    """Run migrations before any worker starts accepting requests."""
    manage = str(BASE_DIR / "manage.py")

    print("[gunicorn] Running database migrations...", flush=True)
    result = subprocess.run(
        [sys.executable, manage, "migrate", "--no-input"],
        capture_output=False,
    )
    if result.returncode != 0:
        print("[gunicorn] migrate failed — continuing anyway", flush=True)

    print("[gunicorn] Running seed command...", flush=True)
    subprocess.run(
        [sys.executable, manage, "seed_bulk_campus"],
        capture_output=False,
    )
    print("[gunicorn] Startup tasks complete.", flush=True)


# Workers and timeout
workers = 2
timeout = 120
