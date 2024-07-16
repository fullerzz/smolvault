#!/bin/bash

# poetry run uvicorn src.smolvault.main:app --log-config=log_conf.yaml --host 0.0.0.0 --server-header --timeout-keep-alive=120
poetry run hypercorn src.smolvault.main:app -b 0.0.0.0 --debug --log-config=logging.conf --log-level=DEBUG --access-logfile=hypercorn.access.log --error-logfile=hypercorn.error.log --keep-alive=120 --workers=1
