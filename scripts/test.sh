#!/bin/bash

export SMOLVAULT_BUCKET="test-bucket"
export SMOLVAULT_DB="test.db"
export SMOLVAULT_CACHE="./uploads/"
export AUTH_SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # key from FastAPI docs to use in tests
export DAILY_UPLOAD_LIMIT_BYTES="50000"
export USERS_LIMIT="20"
export USER_WHITELIST="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"

# remove test db if it exists
if [ -f $SMOLVAULT_DB ]; then
    rm $SMOLVAULT_DB
fi

# remove local cache if it exists
if [ -f $SMOLVAULT_CACHE ]; then
    rm -rf $SMOLVAULT_CACHE
fi

# create local cache dir
mkdir uploads

pytest -vvv tests
