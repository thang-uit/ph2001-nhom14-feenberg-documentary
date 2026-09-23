#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"
input_file="${VOICE_INPUT:-${project_dir}/audio/vo/VO_CHATGPT_170WPM_48K.wav}"
output_file="${VOICE_OUTPUT:-${project_dir}/audio/vo/VO_FINAL_48K.wav}"
probe_file="${project_dir}/qa/voice_final_ffprobe.json"
loudness_file="${project_dir}/qa/voice_final_loudness.txt"

command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null
[[ -f "${input_file}" ]] || { print -u2 "Voice input missing: ${input_file}"; exit 1; }
mkdir -p "${output_file:h}" "${probe_file:h}"

# The locked TTS performance is clean; this is intentionally a light master.
# Avoid aggressive denoising/de-essing that could damage Vietnamese initials.
ffmpeg -hide_banner -loglevel error -y -i "${input_file}" \
  -af "highpass=f=72,equalizer=f=235:t=q:w=1.1:g=-1.2,equalizer=f=3200:t=q:w=1.2:g=0.8,acompressor=threshold=0.14:ratio=1.8:attack=20:release=190,loudnorm=I=-20:TP=-3:LRA=6" \
  -ar 48000 -ac 2 -c:a pcm_s24le "${output_file}"

ffprobe -v error \
  -show_entries format=filename,duration,size,bit_rate:stream=codec_name,sample_rate,channels,bits_per_sample \
  -of json "${output_file}" > "${probe_file}"
ffmpeg -hide_banner -i "${output_file}" -filter_complex ebur128=peak=true \
  -f null - 2> "${loudness_file}"

print "Final voice master: ${output_file}"
