#!/bin/bash

if [ "$DEBUGPY_ENABLED" = "true" ]; then
    echo "Starting Odoo with Debugger (debugpy)..."
    exec python -Xfrozen_modules=off -m debugpy --listen ${DEBUGPY_LISTEN_ADDRESS:-0.0.0.0:5678} --wait-for-client \
        $(which odoo) --workers=0 --max-cron-threads=0 --dev=${ODOO_DEV_MODES:-all}
else
    echo "Starting Odoo in normal mode..."
    exec $(which odoo) --dev=${ODOO_DEV_MODES:-all}
fi
