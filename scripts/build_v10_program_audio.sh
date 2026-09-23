#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"

content_duration="${CONTENT_DURATION:-965.066667}"
credit_duration="${CREDIT_DURATION:-54.100000}"
crossfade="${CROSSFADE:-0.800000}"
final_duration="${FINAL_DURATION:-1018.366667}"
content_audio="${CONTENT_AUDIO:-${project_dir}/audio/mix/FULL_MIX_V10_CONTENT_48K.wav}"
credit_video="${CREDIT_VIDEO:-${project_dir}/CREDIT_TPHCM_OH_YEAH_V4.mp4}"
output_audio="${OUTPUT_AUDIO:-${project_dir}/audio/mix/FULL_MIX_V10_PROGRAM_48K.wav}"
review_audio="${REVIEW_AUDIO:-${project_dir}/audio/mix/FULL_MIX_V10_PROGRAM_REVIEW.m4a}"
probe_file="${PROBE_FILE:-${project_dir}/qa/v10/audio/program_mix_probe.json}"
report_file="${REPORT_FILE:-${project_dir}/qa/v10/audio/program_mix_loudness.txt}"

[[ -f "${content_audio}" ]] || { print -u2 "Missing content mix: ${content_audio}"; exit 1; }
[[ -f "${credit_video}" ]] || { print -u2 "Missing credit artifact: ${credit_video}"; exit 1; }
mkdir -p "${output_audio:h}" "${review_audio:h}" "${probe_file:h}" "${report_file:h}"

ffmpeg -hide_banner -loglevel error -y \
  -i "${content_audio}" -i "${credit_video}" \
  -filter_complex \
    "[0:a]aresample=48000,atrim=0:${content_duration},asetpts=PTS-STARTPTS[content];\
     [1:a]aresample=48000,atrim=0:${credit_duration},asetpts=PTS-STARTPTS[credit];\
     [content][credit]acrossfade=d=${crossfade}:c1=qsin:c2=qsin,atrim=duration=${final_duration},\
     loudnorm=I=-16:TP=-2:LRA=8:linear=true[out]" \
  -map "[out]" -ar 48000 -ac 2 -c:a pcm_s24le "${output_audio}"

ffmpeg -hide_banner -loglevel error -y -i "${output_audio}" \
  -c:a aac -profile:a aac_low -b:a 320k -ar 48000 -ac 2 "${review_audio}"

ffprobe -v error \
  -show_entries format=filename,duration,size,bit_rate:stream=codec_name,sample_rate,channels,bits_per_sample \
  -of json "${output_audio}" > "${probe_file}"
ffmpeg -hide_banner -nostats -i "${output_audio}" -filter_complex ebur128=peak=true \
  -f null - 2> "${report_file}"

print "V10 programme audio: ${output_audio}"
print "V10 programme audio review: ${review_audio}"
