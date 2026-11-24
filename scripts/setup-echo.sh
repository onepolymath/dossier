#!/usr/bin/env bash
# Create a local OpenMinion echo config (no model, no credentials).
# Echo is for wiring and diagnostics, not a qualifying model-backed demo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/lib.sh"
openminion --home-root "$OPENMINION_HOME" --data-root "$OPENMINION_DATA_ROOT" \
  config init --provider echo --force --storage-location config
echo "Echo config written under $OPENMINION_DATA_ROOT"
echo "This does not call a real model. For a qualifying demo, configure Ollama or Cortensor Portal."
