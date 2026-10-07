#!/usr/bin/env bash
# Repository-local setup. Does not synthesize voice, rebuild DOCX or render film.
set -euo pipefail
cd "$(dirname "$0")"

task_python="${PYTHON_BIN:-python3}"
task_skip_browser=false
if [[ "${1:-}" == "--skip-browser" && $# -eq 1 ]]; then
  task_skip_browser=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: ./setup.sh [--skip-browser]" >&2
  exit 2
fi
command -v "$task_python" >/dev/null || { echo "Python not found: $task_python" >&2; exit 1; }
command -v npm >/dev/null || { echo "Node.js/npm is required (Node 22+ recommended)." >&2; exit 1; }
command -v git-lfs >/dev/null || { echo "Install Git LFS and run git lfs pull first." >&2; exit 1; }
[[ "$(uname -s)" == Darwin ]] || { echo "This film requires macOS and Avenir Next." >&2; exit 1; }
[[ -f '/System/Library/Fonts/Avenir Next.ttc' ]] || { echo "Avenir Next font is missing." >&2; exit 1; }
"$task_python" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
node -e 'if (Number(process.versions.node.split(".")[0]) < 18) process.exit(1)'

if [[ -n "${EXTRA_CA_BUNDLE:-}" ]]; then
  [[ -f "$EXTRA_CA_BUNDLE" ]] || { echo "EXTRA_CA_BUNDLE is not a file." >&2; exit 1; }
  export NODE_EXTRA_CA_CERTS="$EXTRA_CA_BUNDLE" PIP_CERT="$EXTRA_CA_BUNDLE"
fi
"$task_python" -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/verify_repository.py

pushd remotion >/dev/null
npm ci --loglevel=error
if [[ "$task_skip_browser" == false ]]; then
  npx --no-install remotion browser ensure
fi
popd >/dev/null

# Only reconstructs deterministic preview assets and SRT; video/DOCX stay intact.
.venv/bin/python scripts/v13_film.py export
echo "Setup complete. See README.md for preview and render commands."
