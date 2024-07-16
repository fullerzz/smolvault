#!/bin/bash

poetry run uvicorn src.smolvault.main:app --log-config=log_conf.yaml --host 0.0.0.0

