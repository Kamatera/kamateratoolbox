#!/usr/bin/env bash

QUEUE_ID="${1}"

[ "${QUEUE_ID}" == "" ] && echo missing QUEUE_ID arg && exit 1

tests/curl/cloudcli_server_request.sh GET "service/queue?id=${QUEUE_ID}"