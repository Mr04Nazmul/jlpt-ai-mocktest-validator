#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements.txt
sudo apt-get update -qq
sudo apt-get install -y fonts-noto-cjk poppler-utils
if ! command -v ollama >/dev/null; then
  curl --fail --location https://ollama.com/install.sh -o /tmp/ollama-install.sh
  sh /tmp/ollama-install.sh
fi
mkdir -p data
