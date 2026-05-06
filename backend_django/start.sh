#!/usr/bin/env bash
# Render start script for technopath-backend
# Gunicorn binds the port first, then on_starting hook runs migrate before workers start
set -e
exec gunicorn technopath.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --config gunicorn.conf.py \
    --log-level info
