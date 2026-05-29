#!/usr/bin/env bash
# Full local dev pipeline — reference kernel + reports
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

echo "== install =="
pip install -e ".[test]" -q

echo "== config sync =="
python scripts/sync_config_check.py

echo "== pytest =="
pytest -q

echo "== tuning sweep =="
python scripts/tuning_sweep.py

echo "== sim report =="
python scripts/sim_report.py

echo "== lattice export =="
python scripts/lattice_export.py --oval -o output/track_lattice.json

echo "== engine manifest =="
python scripts/engine_manifest.py

echo "== headless play =="
python scripts/headless_play.py --profile smooth --seconds 10

echo ""
echo "Done. Full local: ./scripts/local_run.sh --rojo"
echo "Docs: docs/LOCAL_RUN.md"
