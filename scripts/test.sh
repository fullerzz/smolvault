#!/bin/bash

export SMOLVAULT_BUCKET="test-bucket"
export SMOLVAULT_DB="test.db"
export SMOLVAULT_CACHE="./uploads/"

# remove test db if it exists
if [ -f $SMOLVAULT_DB ]; then
    rm $SMOLVAULT_DB
fi

# remove local cache if it exists
if [ -f $SMOLVAULT_CACHE ]; then
    rm -rf $SMOLVAULT_CACHE
fi

poetry run pytest -v tests/
