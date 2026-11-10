#!/usr/bin/env bash
# Run the whole suite on your Mac (no Docker, no Jenkins).
#   bash scripts/run_tests_local.sh            all tests, headless
#   bash scripts/run_tests_local.sh -m api     API tests only
#   HEADED=1 bash scripts/run_tests_local.sh   watch Chrome do the Selenium UI tests
#   bash scripts/run_tests_local.sh -m playwright   Playwright UI tests only
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/python ]; then
  echo "Creating virtual environment in .venv ..."
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt
.venv/bin/playwright install chromium   # no-op once Playwright's Chromium is downloaded

mkdir -p reports
.venv/bin/pytest --junitxml=reports/results.xml "$@"
