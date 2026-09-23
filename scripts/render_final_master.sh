#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"
duration="${DURATION:-933.366667}"

picture_file="${PICTURE_FILE:-${project_dir}/renders/PICTURE_MASTER_1080P_VALE_V5.mp4}"
audio_file="${AUDIO_FILE:-${project_dir}/audio/mix/FULL_MIX_DELIVERY_V5_48K.wav}"
srt_file="${SRT_FILE:-${project_dir}/05_subtitles.srt}"
work_dir="${WORK_DIR:-${project_dir}/video/final_work/subtitles}"
subtitle_file="${SUBTITLE_FILE:-${work_dir}/SUBTITLE_ALPHA_1080P.mov}"
output_file="${OUTPUT_FILE:-${project_dir}/renders/FINAL_FEENBERG_DOCUMENTARY_VALE_V5_candidate.mp4}"

command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null
[[ -f "${picture_file}" ]] || { print -u2 "Picture master missing: ${picture_file}"; exit 1; }
[[ -f "${audio_file}" ]] || { print -u2 "Final audio mix missing: ${audio_file}"; exit 1; }
[[ -f "${srt_file}" ]] || { print -u2 "Subtitle file missing: ${srt_file}"; exit 1; }

mkdir -p "${work_dir}" "${output_file:h}"

python3 "${script_dir}/build_subtitle_overlay.py" \
  --srt "${srt_file}" \
  --output "${subtitle_file}" \
  --work-dir "${work_dir}/frames" \
  --duration "${duration}"

# The picture master is already graded and frame-locked.  This pass burns the
# deterministic Vietnamese subtitle layer, adds the mastered mix, and writes a
# YouTube-ready SDR file.  H.264 VUI metadata is written explicitly because the
# VideoToolbox encoder does not reliably expose all Rec.709 fields by itself.
ffmpeg -hide_banner -loglevel error -y \
  -i "${picture_file}" \
  -i "${subtitle_file}" \
  -i "${audio_file}" \
  -filter_complex \
    "[0:v]setpts=PTS-STARTPTS[base];[1:v]setpts=PTS-STARTPTS[sub];[base][sub]overlay=0:0:format=auto:eof_action=pass,trim=duration=${duration},fps=30,setsar=1,format=yuv420p[outv]" \
  -map "[outv]" -map 2:a:0 \
  -t "${duration}" \
  -c:v h264_videotoolbox -profile:v high -level:v 4.2 \
  -b:v 18M -maxrate 24M -bufsize 36M -g 60 -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 \
  -bsf:v "h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1" \
  -c:a aac -profile:a aac_low -b:a 320k -ar 48000 -ac 2 \
  -movflags +faststart -tag:v avc1 \
  "${output_file}"

print "Final candidate rendered: ${output_file}"
