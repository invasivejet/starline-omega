#!/usr/bin/env bash
# STARLINE Ω — one-command local development
# Usage:
#   ./scripts/local_run.sh           # validate + headless demo
#   ./scripts/local_run.sh --rojo    # also start rojo serve (background)
#   ./scripts/local_run.sh --full    # validate + headless + telemetry server
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

ROJO=0
FULL=0
for arg in "$@"; do
  case "$arg" in
    --rojo) ROJO=1 ;;
    --full) FULL=1; ROJO=1 ;;
  esac
done

echo "╔══════════════════════════════════════╗"
echo "║  STARLINE Ω — local development      ║"
echo "╚══════════════════════════════════════╝"

# --- Python env ---
if [[ ! -d .venv ]]; then
  echo "→ creating .venv"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -e ".[test]" -q

echo "→ config sync check"
python scripts/sync_config_check.py

echo "→ pytest"
pytest -q

echo "→ tuning sweep"
python scripts/tuning_sweep.py

echo "→ loop seal (Schrödingerized lattice)"
python scripts/loop_seal.py

echo "→ engine manifest"
python scripts/engine_manifest.py

echo "→ coherence loop (closed measurement)"
python scripts/coherence_loop.py

echo "→ field emergence report (Phase II)"
python scripts/field_report.py

echo "→ AFK report"
python scripts/afk_report.py

echo "→ headless play (smooth 15s)"
python scripts/headless_play.py --profile smooth --seconds 15 --wire-log output/wires_smooth.jsonl

if [[ "$FULL" == "1" ]]; then
  echo "→ telemetry server (background :8765)"
  python scripts/telemetry_server.py --port 8765 &
  TEL_PID=$!
  echo "   PID $TEL_PID — kill with: kill $TEL_PID"
fi

if [[ "$ROJO" == "1" ]]; then
  if command -v rojo >/dev/null 2>&1; then
    echo "→ rojo serve (background :34872 default)"
    rojo serve &
    ROJO_PID=$!
    echo "   PID $ROJO_PID"
    echo ""
    echo "   Studio: Rojo plugin → Connect → Play (F5)"
  else
    echo "⚠ rojo not in PATH — install: https://rojo.space/docs/install"
    echo "  Or copy roblox/ manually per roblox/README.md"
  fi
fi

echo ""
echo "════════════════════════════════════════"
echo "Local runtimes:"
echo "  1. Headless sim  — python scripts/headless_play.py"
echo "  2. Roblox Studio — rojo serve + Play"
echo "  3. Telemetry     — python scripts/telemetry_server.py"
echo ""
echo "Docs: docs/LOCAL_RUN.md"
echo "Output: output/headless_session.json"
echo "════════════════════════════════════════"
