#!/usr/bin/env bash
# Project-local OpenMinion paths. Source from the other scripts.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OPENMINION_HOME="${OPENMINION_HOME:-$ROOT/.om-home}"
export OPENMINION_DATA_ROOT="${OPENMINION_DATA_ROOT:-$ROOT/.om-home/.openminion}"
export PATH="$ROOT/.venv/bin:$PATH"
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi
if [[ "$OPENMINION_HOME" == *"/home/box/secure"* || "$OPENMINION_DATA_ROOT" == *"/home/box/secure"* \
   || "$OPENMINION_HOME" == *"/home/box/.local/share"* || "$OPENMINION_DATA_ROOT" == *"/home/box/.local/share"* ]]; then
  echo "refusing to use a forbidden home or data root" >&2
  exit 1
fi
mkdir -p "$OPENMINION_HOME" "$OPENMINION_DATA_ROOT"
