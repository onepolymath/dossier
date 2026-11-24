#!/usr/bin/env bash
# Configure Cortensor Portal. Requires a CORTENSOR_API_KEY (Portal access is
# optional for qualification and is coordinated by the hackathon team).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/lib.sh"
if [[ -z "${CORTENSOR_API_KEY:-}" ]]; then
  echo "Set CORTENSOR_API_KEY in .env first. Do not commit it. Portal access is optional." >&2
  exit 1
fi
MODEL="${1:-oss-20b}"
openminion --home-root "$OPENMINION_HOME" --data-root "$OPENMINION_DATA_ROOT" \
  setup --provider cortensor-portal --model "$MODEL" --agent cortensor-portal --no-chat
echo "Configured Cortensor Portal. Export DOSSIER_AGENT_ID=cortensor-portal"
