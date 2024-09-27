#!/bin/bash

source .venv/bin/activate
hypercorn src.smolvault.main:app -b 0.0.0.0:8200 --debug \
    --log-config=logging.conf --log-level=DEBUG \
    --access-logfile=hypercorn.access.log \
    --error-logfile=hypercorn.error.log \
    --keep-alive=120 --workers=1
