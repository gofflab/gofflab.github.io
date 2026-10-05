#!/usr/bin/env bash
# Preview the site locally after editing data/ or templates/.
#
#   scripts/preview.sh          # build, then serve at http://localhost:8000
#   scripts/preview.sh 8080     # use another port
#
# Builds from the cached publication data without Google Analytics (so your own visits
# aren't counted), serves the repo root, and opens your browser. Press Ctrl-C to stop;
# the normal build, with analytics, is then restored so the pages are safe to commit.
set -euo pipefail
cd "$(dirname "$0")/.."
port="${1:-8000}"

python3 scripts/main.py --offline --no-analytics
trap 'echo; echo "Restoring the normal build (with analytics)..."; python3 scripts/main.py --offline' EXIT

url="http://localhost:$port/"
echo "Previewing at $url  (Ctrl-C to stop)"
( sleep 1; open "$url" 2>/dev/null || xdg-open "$url" 2>/dev/null || true ) &
python3 -m http.server "$port" --bind 127.0.0.1
