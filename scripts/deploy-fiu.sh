#!/usr/bin/env bash

set -euo pipefail

TARGET_HOST="${CAPSTONE_DEPLOY_HOST:-sadjadi@ocelot.aul.fiu.edu}"
TARGET_DIR="${CAPSTONE_DEPLOY_DIR:-~/public_html/Capstone/}"

if [ ! -d "dist" ]; then
  echo "dist/ does not exist. Run npm run build first."
  exit 1
fi

rsync -avz --delete dist/ "${TARGET_HOST}:${TARGET_DIR}"
