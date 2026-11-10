#!/usr/bin/env bash
set -euo pipefail
# Use available RAM, reserve memory for PDF processing and the UI.
kb=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
if (( kb < 2500000 )); then echo "Insufficient available RAM (<2.5 GB); stop other processes."; exit 1
elif (( kb < 4500000 )); then model=qwen2.5:0.5b
elif (( kb < 12000000 )); then model=qwen2.5:1.5b
else model=qwen2.5:3b
fi
ollama pull "$model"
printf '%s' "$model" >data/model.txt
ollama run "$model" "日本語で短く挨拶してください。"
