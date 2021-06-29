#!/bin/bash

set -e

if [ "$MODE" = "TESTING" ]; then
    echo "Run Unit Tests"
    exec pytest -s --verbose -vv --ff
else
    echo "Run Uvicorn in production mode"
    exec uvicorn main:app --host 0.0.0.0 --port 9090 --ws none
fi
