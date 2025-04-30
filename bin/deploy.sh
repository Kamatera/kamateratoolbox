#!/usr/bin/env bash

set -euxo pipefail

rm -rf .data/pages
git clone -b pages https://github.com/Kamatera/kamateratoolbox.git .data/pages
python -m pages_src.generate "$@"
cd .data/pages
git add .
git config user.name "%GIT_USERNAME"
git config user.email "%GIT_EMAIL"
if ! git commit -m "Update pages"; then
  echo "No changes to commit"
else
  AUTH=$(printf "%s:%s" "$GH_USER" "$GH_TOKEN" | base64 -w0)
  git -c http.extraHeader="Authorization: Basic $AUTH" push origin pages
fi
