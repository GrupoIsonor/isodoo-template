#!/bin/bash

if [ "$DEBUGPY_ENABLED" = "true" ]; then
    echo "Starting Odoo with Debugger (debugpy)..."
    exec python -m debugpy --listen ${DEBUGPY_LISTEN_ADDRESS:-0.0.0.0:5678} --wait-for-client -Xfrozen_modules=off \
        $(which odoo) --workers=0 --dev=all --log-level=debug
else
    echo "Starting Odoo in normal mode..."
    exec odoo
fi
