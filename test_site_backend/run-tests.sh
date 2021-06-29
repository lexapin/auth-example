#!/usr/bin/env bash

printf "Preparing docker-compose image\n"

docker-compose -f ./docker-compose-test.yaml -p ci build

printf "Running unit tests inside docker-compose container\n"

docker-compose -f ./docker-compose-test.yaml -p ci up --abort-on-container-exit --exit-code-from backend

docker logs -f ci_backend_1

if [ $(docker wait ci_backend_1) -gt 0 ];
then
	echo "BACKEND_TESTS_FAILURE"
    exit 1
else
	echo "BACKEND_TESTS_SUCCESS"
fi
