#!/usr/bin/env bash

REQ_JSON="${1}"

[ "${REQ_JSON}" == "" ] && echo missing REQ_JSON arg && exit 1

tests/curl/cloudcli_server_request.sh POST service/server "${REQ_JSON}"