#!/usr/bin/env bash

set -euo pipefail

curl \
  -XPOST \
  -H "AuthClientId: ${KAMATERA_API_CLIENT_ID}" \
  -H "AuthSecret: ${KAMATERA_API_SECRET}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "datacenter": "'${SERVER_DATACENTER}'",
    "nServers": 1,
    "names": ["'${SERVER_NAME}'"],
    "cpuStr": "2B",
    "cpuType": "B",
    "ramMB": "2048",
    "diskSizesGB": ["50"],
    "password": "'${SERVER_PASSWORD}'",
    "passwordValidate": "'${SERVER_PASSWORD}'",
    "managed": false,
    "backup": false,
    "billingMode": 1,
    "trafficPackage": "",
    "useSimpleNetworking": false,
    "powerOnCompletion": true,
    "useSimpleWan": false,
    "useSimpleLan": false,
    "netModes": ["wan"],
    "netNames": ["auto"],
    "netSubnets": [""],
    "netPrefixes": [0],
    "netIps": ["auto"],
    "diskImageId": "'${SERVER_IMAGE}'",
    "sourceServerId": "",
    "userId": 0,
    "ownerId": 0,
    "srcUI": false,
    "selectedKey": null,
    "script": "",
    "selectedSSHKeyValue": "'"$(cat ~/.ssh/id_rsa.pub)"'",
    "selectedTags": [],
    "userData": ""
  }' "https://console.kamatera.com/svc/serverCreate"
