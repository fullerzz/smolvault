#!/bin/bash

gunicorn src.smolvault.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker
