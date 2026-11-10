#!/usr/bin/env bash
set -euo pipefail
mkdir -p data
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export CUDA_VISIBLE_DEVICES=""
if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null; then
  nohup ollama serve >data/ollama.log 2>&1 &
fi
if ! curl -sf http://127.0.0.1:8501/_stcore/health >/dev/null; then
  nohup python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.maxUploadSize 20 --browser.gatherUsageStats false >data/web.log 2>&1 &
fi
