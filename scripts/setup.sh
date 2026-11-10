#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements.txt
if ! command -v ollama >/dev/null; then
  curl --fail --location https://ollama.com/install.sh -o /tmp/ollama-install.sh
  sh /tmp/ollama-install.sh
fi
mkdir -p data
