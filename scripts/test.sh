#!/bin/bash

export SMOLVAULT_BUCKET="test-bucket"
export SMOLVAULT_DB="test.db"
poetry run pytest tests/
