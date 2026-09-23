#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"

duration="${DURATION:-965.066667}"
voice_file="${VOICE_FILE:-${project_dir}/audio/vo/vale_unified_v9/VO_VALE_UNIFIED_V9_WITH_BREATHS_48K.wav}"
music_file="${MUSIC_FILE:-${project_dir}/audio/music/SCORE_SUNO_V8_48K.wav}"
sfx_file="${SFX_FILE:-${project_dir}/audio/sfx/SFX_AMBIENCE_V10_48K.wav}"
output_file="${OUTPUT_FILE:-${project_dir}/audio/mix/FULL_MIX_V10_CONTENT_48K.wav}"
review_file="${REVIEW_FILE:-${project_dir}/audio/mix/FULL_MIX_V10_CONTENT_REVIEW.m4a}"
probe_file="${PROBE_FILE:-${project_dir}/qa/v10/audio/content_mix_probe.json}"
report_file="${REPORT_FILE:-${project_dir}/qa/v10/audio/content_mix_loudness.txt}"

for input_file in "${voice_file}" "${music_file}" "${sfx_file}"; do
  [[ -f "${input_file}" ]] || { print -u2 "Missing V10 audio input: ${input_file}"; exit 1; }
done

mkdir -p "${output_file:h}" "${review_file:h}" "${probe_file:h}" "${report_file:h}"

# The score remains audible in the deliberate narration gaps and ducks at
# phrase level.  The final 2.8 seconds resolve under the spoken thanks before
# the separate Oh Yeah credit master enters through the final crossfade.
fade_start="${MUSIC_FADE_START:-962.266667}"
music_gain="${MUSIC_GAIN:-0.18}"
sfx_gain="${SFX_GAIN:-0.14}"

ffmpeg -hide_banner -loglevel error -y \
  -i "${voice_file}" -i "${music_file}" -i "${sfx_file}" \
  -filter_complex \
    "[0:a]aresample=48000,highpass=f=75,equalizer=f=180:t=q:w=0.8:g=-1.4,equalizer=f=3000:t=q:w=1.1:g=2.0,acompressor=threshold=0.12:ratio=2.2:attack=18:release=180,apad=whole_dur=${duration},atrim=0:${duration},asplit=2[voice][key];\
     [1:a]aresample=48000,atrim=0:${duration},volume=${music_gain},afade=t=out:st=${fade_start}:d=2.8[music];\
     [music][key]sidechaincompress=threshold=0.012:ratio=5:attack=110:release=520[ducked];\
     [2:a]aresample=48000,atrim=0:${duration},volume=${sfx_gain}[sfx];\
     [voice][ducked][sfx]amix=inputs=3:normalize=0,alimiter=limit=0.82:attack=5:release=90,atrim=0:${duration},loudnorm=I=-16:TP=-2:LRA=8[mix]" \
  -map "[mix]" -ar 48000 -ac 2 -c:a pcm_s24le "${output_file}"

ffmpeg -hide_banner -loglevel error -y -i "${output_file}" \
  -c:a aac -profile:a aac_low -b:a 256k -ar 48000 -ac 2 "${review_file}"

ffprobe -v error \
  -show_entries format=filename,duration,size,bit_rate:stream=codec_name,sample_rate,channels,bits_per_sample \
  -of json "${output_file}" > "${probe_file}"

ffmpeg -hide_banner -nostats -i "${output_file}" -filter_complex ebur128=peak=true \
  -f null - 2> "${report_file}"

print "V10 content mix: ${output_file}"
print "V10 content mix review: ${review_file}"
