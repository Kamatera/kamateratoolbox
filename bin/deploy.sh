#!/usr/bin/env bash

set -euxo pipefail

uv sync
rm -rf .data/pages
git clone -b pages git@github.com:Kamatera/kamateratoolbox.git .data/pages
uv run -m pages_src.generate
cd .data/pages
git add .
if ! git commit -m "Update pages"; then
  echo "No changes to commit"
else
  git push origin pages
fi
