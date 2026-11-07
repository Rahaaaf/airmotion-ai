#!/usr/bin/env bash
set -e

python -m pip install --upgrade pip
pip install "fastapi[all]" uvicorn tensorflow numpy scikit-learn matplotlib requests pyserial

cd /workspaces/airmotion-ai/frontend || true
if [ -f package.json ]; then
  npm install
fi
