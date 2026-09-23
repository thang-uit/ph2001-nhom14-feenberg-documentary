#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"
source_file="${SOURCE_FILE:-${project_dir}/Feenberg-NhacNen.mp3}"
output_file="${OUTPUT_FILE:-${project_dir}/audio/music/SCORE_SUNO_V8_48K.wav}"
duration="${DURATION:-972.566667}"
loop_end="${LOOP_END:-171.5}"
crossfade="${CROSSFADE:-5.5}"

command -v ffmpeg >/dev/null
[[ -f "${source_file}" ]] || { print -u2 "Music source missing: ${source_file}"; exit 1; }
mkdir -p "${output_file:h}"

# The source naturally resolves near 171.5 seconds. Six trimmed copies with a
# long equal-power crossfade cover the complete programme while keeping every
# repeat boundary below the narration. Normalization happens before looping so
# each copy has identical energy; the final fade belongs only to the end credit.
inputs=()
for _index in {1..6}; do
  inputs+=( -i "${source_file}" )
done

filter=""
for index in {0..5}; do
  filter+="[${index}:a]atrim=0:${loop_end},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,loudnorm=I=-18:TP=-2:LRA=10[a${index}];"
done
filter+="[a0][a1]acrossfade=d=${crossfade}:c1=qsin:c2=qsin[x1];"
for index in {2..5}; do
  previous=$((index - 1))
  filter+="[x${previous}][a${index}]acrossfade=d=${crossfade}:c1=qsin:c2=qsin[x${index}];"
done
fade_out_start=$(python3 -c "print(max(0.0, float('${duration}') - 7.0))")
filter+="[x5]atrim=0:${duration},afade=t=in:st=0:d=2.0,afade=t=out:st=${fade_out_start}:d=7.0,alimiter=limit=0.794:attack=5:release=100[out]"

ffmpeg -hide_banner -loglevel error -y \
  "${inputs[@]}" \
  -filter_complex "${filter}" \
  -map "[out]" -ar 48000 -ac 2 -c:a pcm_s24le \
  "${output_file}"

print "Suno V8 score created: ${output_file}"
