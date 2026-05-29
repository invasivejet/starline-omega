#!/usr/bin/env bash
# STARLINE Ω — final test-drive validation (run before Studio Play)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  STARLINE Ω — TEST DRIVE VALIDATION                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# --- Python env ---
if [[ ! -d .venv ]]; then
  echo "→ creating .venv"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -e ".[test]" -q

echo "→ [1/6] config sync"
python scripts/sync_config_check.py

echo "→ [2/6] pytest (40 tests)"
pytest -q

echo "→ [3/6] loop seal"
python scripts/loop_seal.py

echo "→ [4/6] coherence loop"
python scripts/coherence_loop.py

echo "→ [5/6] field report"
python scripts/field_report.py

echo "→ [6/6] headless drive (30s)"
python scripts/headless_play.py --profile smooth --seconds 30

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  HEADLESS: PASS"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  STUDIO TEST DRIVE (interactive):"
echo ""
echo "  Terminal 1:"
echo "    cd $ROOT"
echo "    rojo serve"
echo ""
echo "  Roblox Studio:"
echo "    1. Install Rojo plugin (https://rojo.space/docs/install)"
echo "    2. New place → Rojo → Connect (localhost:34872)"
echo "    3. Game Settings → Security → Enable Studio API Services"
echo "    4. Press Play (F5)"
echo ""
echo "  You should see:"
echo "    • Blue glowing track (StarlineTrackVisual)"
echo "    • HUD top-left (ℛ, c, flow)"
echo "    • Output: [Starline] perf server | sim 60 Hz ..."
echo ""
echo "  Controls: WASD · B garage · F AFK · U circuit · 1 oval · 2 circuit"
echo ""
echo "  Full guide: docs/TEST_DRIVE.md"
echo "════════════════════════════════════════════════════════════"

if command -v rojo >/dev/null 2>&1; then
  echo ""
  read -r -p "Start rojo serve now? [y/N] " ans || true
  if [[ "${ans,,}" == "y" ]]; then
    exec rojo serve
  fi
else
  echo ""
  echo "  Install Rojo for Studio sync:"
  echo "    curl -sSf https://raw.githubusercontent.com/rojo-rbx/rojo/master/scripts/install.sh | bash"
  echo "    # then re-run: ./scripts/test_drive.sh"
fi
