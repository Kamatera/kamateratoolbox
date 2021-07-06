#!/usr/bin/env bash

SERVER_NAME="${1}"

[ "${SERVER_NAME}" == "" ] && echo missing SERVER_NAME arg && exit 1

tests/curl/cloudcli_server_request.sh POST "service/server/ssh" '{"name":"'"${SERVER_NAME}"'"}'