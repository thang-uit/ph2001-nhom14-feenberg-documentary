#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"

python3 "${script_dir}/build_original_score.py" \
  --output "${project_dir}/audio/music/MUSIC_ORIGINAL_SCORE_48K.wav" \
  --work-dir "${project_dir}/audio/music/synthesis_work" \
  --report "${project_dir}/qa/original_score_ffprobe.json"

ffmpeg -hide_banner -loglevel error -y \
  -i "${project_dir}/audio/music/MUSIC_ORIGINAL_SCORE_48K.wav" \
  -t 45 \
  -c:a pcm_s24le -ar 48000 -ac 2 \
  "${project_dir}/audio/music/MUSIC_PROOF_0000_0045_48K.wav"

print "Proof excerpt: ${project_dir}/audio/music/MUSIC_PROOF_0000_0045_48K.wav"
