#!/usr/bin/env bash
# Configure the free, local Ollama provider. Install Ollama first:
#   https://ollama.com/download
# Then pull a tool-capable model, for example: ollama pull llama3.2:3b
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/lib.sh"
MODEL="${1:-llama3.2:3b}"
if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed. Install it from https://ollama.com/download (free, local, no account required), then re-run." >&2
  exit 1
fi
openminion --home-root "$OPENMINION_HOME" --data-root "$OPENMINION_DATA_ROOT" \
  setup --provider ollama --model "$MODEL" --agent dossier --no-chat
echo "Configured Ollama model '$MODEL'."
echo "Run: dossier inspect --agent fixtures/samples/payroll_lure.eml"
