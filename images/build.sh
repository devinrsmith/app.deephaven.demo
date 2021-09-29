#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker build \
    --build-arg "BASE=${SERVER_BASE:-deephaven/grpc-api:local-build}" \
    --tag deephaven/custom-server \
    "${__dir}/custom-server"

docker build \
    --build-arg "BASE=${WEB_BASE:-deephaven/web:local-build}" \
    --tag deephaven/custom-web \
    "${__dir}/custom-web"
