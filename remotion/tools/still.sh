#!/bin/bash
# Render QA stills of one graphic: tools/still.sh <graphic-name> [fractions...]
# Frames are taken at the given fractions of the shot (default 0.25 0.6 0.95); output → out/qa/<name>_<frac>.png
set -euo pipefail
cd "$(dirname "$0")/.."
name="$1"; shift
fracs=("${@:-0.25 0.6 0.95}")
read -r index frames <<<"$(node -e '
const f=require("./src/data/film.json"); const n=process.argv[1];
const i=f.shots.findIndex(s=>s.ref===n); if(i<0){console.error("no shot uses "+n);process.exit(1)}
console.log(i, f.shots[i].frames);' "$name")"
mkdir -p out/qa
for fr in ${fracs[@]}; do
  frame=$(node -e "console.log(Math.min($frames-1, Math.round($frames*$fr)))")
  npx remotion still Shot "out/qa/${name}_${fr}.png" --props="{\"index\":$index}" --frame="$frame" --public-dir=public_gfx --log=error >/dev/null
  echo "out/qa/${name}_${fr}.png (shot $index, frame $frame/$frames)"
done
