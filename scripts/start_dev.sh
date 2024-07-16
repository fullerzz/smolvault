#!/bin/bash

poetry run uvicorn src.smolvault.main:app --reload --log-config=log_conf.yaml
