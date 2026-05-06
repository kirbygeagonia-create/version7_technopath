"""
Gunicorn configuration for Render deployment.
Runs Django migrations before workers start (on_starting hook),
so the port binds immediately while DB setup happens in the master process.
"""
import os
import subprocess
import sys

# Set a marker so apps.py ready() hooks know we're in gunicorn runtime
os.environ.setdefault('SERVER_SOFTWARE', 'gunicorn')


def on_starting(server):
    """Run migrations before any worker starts accepting requests."""
    print("[gunicorn] Running database migrations...", flush=True)
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--no-input"],
        capture_output=False,
    )
    if result.returncode != 0:
        print("[gunicorn] migrate failed — continuing anyway", flush=True)

    print("[gunicorn] Running seed command...", flush=True)
    subprocess.run(
        [sys.executable, "manage.py", "seed_bulk_campus"],
        capture_output=False,
    )
    print("[gunicorn] Startup tasks complete.", flush=True)


# Bind is set via --bind CLI arg from Render's $PORT
workers = 2
timeout = 120
