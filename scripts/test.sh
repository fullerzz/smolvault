#!/bin/bash

export SMOLVAULT_BUCKET="test-bucket"
export SMOLVAULT_DB="test.db"

# remove test db if it exists
if [ -f $SMOLVAULT_DB ]; then
    rm $SMOLVAULT_DB
fi

poetry run pytest -vvv tests/
