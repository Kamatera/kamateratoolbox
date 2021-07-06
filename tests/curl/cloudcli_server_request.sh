#!/usr/bin/env bash

[ "${KAMATERA_API_CLIENT_ID}" == "" ] && echo missing KAMATERA_API_CLIENT_ID env var && exit 1
[ "${KAMATERA_API_SECRET}" == "" ] && echo missing KAMATERA_API_SECRET env var && exit 1

REQ_METHOD="${1}"
REQ_PATH="${2}"
REQ_JSON="${3}"

[ "${REQ_METHOD}" == "" ] && echo missing REQ_METHOD arg && exit 1
[ "${REQ_PATH}" == "" ] && echo missing REQ_PATH arg && exit 1

curl \
  -X$REQ_METHOD \
  -H "AuthClientId: ${KAMATERA_API_CLIENT_ID}" \
  -H "AuthSecret: ${KAMATERA_API_SECRET}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "${REQ_JSON}" \
  "https://cloudcli.cloudwm.com/${REQ_PATH}"
