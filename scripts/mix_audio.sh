#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"
duration="${DURATION:-933.366667}"
mode="${MIX_MODE:-final}"
voice_file="${VOICE_FILE:-${project_dir}/audio/vo/VO_VALE_V5_MASTER_48K.wav}"
music_file="${MUSIC_FILE:-${project_dir}/audio/music/MUSIC_ORIGINAL_SCORE_48K.wav}"
sfx_file="${SFX_FILE:-${project_dir}/audio/sfx/SFX_AMBIENCE_SPEECH_ALIGNED_48K.wav}"
music_gain_voice="${MUSIC_GAIN_VOICE:-0.20}"
music_gain_credit="${MUSIC_GAIN_CREDIT:-0.34}"
sfx_gain="${SFX_GAIN:-0.30}"
target_i="${TARGET_I:-16}"
target_tp="${TARGET_TP:--1.5}"
limiter_limit="$(python3 -c "print(10 ** (float('${target_tp}') / 20))")"

if [[ "${mode}" == "draft" ]]; then
  output_file="${OUTPUT_FILE:-${project_dir}/audio/mix/FULL_MIX_DRAFT_48K.wav}"
  review_file="${REVIEW_FILE:-${project_dir}/audio/mix/FULL_MIX_DRAFT_REVIEW.m4a}"
else
  output_file="${OUTPUT_FILE:-${project_dir}/audio/mix/FULL_MIX_DELIVERY_48K.wav}"
  review_file="${REVIEW_FILE:-${project_dir}/audio/mix/FULL_MIX_DELIVERY_REVIEW.m4a}"
fi
report_file="${REPORT_FILE:-${project_dir}/qa/audio_mix_loudness.txt}"
probe_file="${PROBE_FILE:-${project_dir}/qa/audio_mix_ffprobe.json}"

command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null

if [[ ! -f "${voice_file}" ]]; then
  print -u2 "Voice file missing: ${voice_file}"
  exit 1
fi
if [[ ! -f "${music_file}" ]]; then
  print -u2 "Music file missing: ${music_file}"
  exit 1
fi
if [[ "${mode}" == "final" && ! -f "${sfx_file}" ]]; then
  print -u2 "Final ambience/SFX stem missing: ${sfx_file}"
  exit 1
fi

mkdir -p "${output_file:h}" "${review_file:h}" "${report_file:h}" "${probe_file:h}"

# Keep the score restrained under the single Vale narration and let it rise
# gently only after the spoken conclusion. Side-chain compression provides
# phrase-level ducking without pumping or swallowing word endings.
voice_duration="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "${voice_file}")"
# Keep a continuous cinematic bed, but never let the silent credits become a
# second, louder music video.  The V7 score carries its own sparse resolving
# cadence after the spoken thanks, so only a modest lift is needed there.
music_gain="if(lt(t,${voice_duration}),${music_gain_voice},${music_gain_credit})"

if [[ -f "${sfx_file}" ]]; then
  ffmpeg -hide_banner -loglevel error -y \
    -i "${voice_file}" -i "${music_file}" -i "${sfx_file}" \
    -filter_complex \
      "[0:a]aresample=48000,highpass=f=75,equalizer=f=180:t=q:w=0.8:g=-1.4,equalizer=f=3000:t=q:w=1.1:g=2.0,acompressor=threshold=0.12:ratio=2.2:attack=18:release=180,apad=whole_dur=${duration},atrim=0:${duration},asplit=2[voice][key];\
       [1:a]aresample=48000,volume='${music_gain}':eval=frame[music_level];\
       [music_level][key]sidechaincompress=threshold=0.010:ratio=6:attack=70:release=420[ducked];\
       [2:a]aresample=48000,volume=${sfx_gain},apad=whole_dur=${duration},atrim=0:${duration}[sfx];\
       [voice][ducked][sfx]amix=inputs=3:normalize=0,alimiter=limit=${limiter_limit}:attack=5:release=80,atrim=0:${duration},loudnorm=I=-${target_i}:TP=${target_tp}:LRA=8[mix]" \
    -map "[mix]" -ar 48000 -ac 2 -c:a pcm_s24le "${output_file}"
else
  ffmpeg -hide_banner -loglevel error -y \
    -i "${voice_file}" -i "${music_file}" \
    -filter_complex \
      "[0:a]aresample=48000,highpass=f=75,equalizer=f=180:t=q:w=0.8:g=-1.4,equalizer=f=3000:t=q:w=1.1:g=2.0,acompressor=threshold=0.12:ratio=2.2:attack=18:release=180,apad=whole_dur=${duration},atrim=0:${duration},asplit=2[voice][key];\
       [1:a]aresample=48000,volume='${music_gain}':eval=frame[music_level];\
       [music_level][key]sidechaincompress=threshold=0.012:ratio=5:attack=110:release=520[ducked];\
       [voice][ducked]amix=inputs=2:normalize=0,alimiter=limit=${limiter_limit}:attack=5:release=80,atrim=0:${duration},loudnorm=I=-${target_i}:TP=${target_tp}:LRA=8[mix]" \
    -map "[mix]" -ar 48000 -ac 2 -c:a pcm_s24le "${output_file}"
fi

ffmpeg -hide_banner -loglevel error -y -i "${output_file}" \
  -c:a aac -b:a 256k -ar 48000 "${review_file}"

ffprobe -v error \
  -show_entries format=filename,duration,size,bit_rate:stream=codec_name,sample_rate,channels,bits_per_sample \
  -of json "${output_file}" > "${probe_file}"

ffmpeg -hide_banner -i "${output_file}" -filter_complex ebur128=peak=true \
  -f null - 2> "${report_file}"

print "Audio mix created: ${output_file}"
print "Review audio: ${review_file}"
print "Loudness report: ${report_file}"
