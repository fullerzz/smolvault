#!/bin/bash

poetry run gunicorn src.smolvault.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
