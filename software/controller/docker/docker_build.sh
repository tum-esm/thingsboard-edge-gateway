#!/bin/bash

# Build the docker image
docker build -t tum-esm/acropolis/edge-node -f $(dirname "$0")/Dockerfile $(dirname "$0")/../