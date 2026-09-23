#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"

content_duration="${CONTENT_DURATION:-965.066667}"
credit_duration="${CREDIT_DURATION:-54.100000}"
crossfade="${CROSSFADE:-0.800000}"
crossfade_offset="${CROSSFADE_OFFSET:-964.266667}"
final_duration="${FINAL_DURATION:-1018.366667}"
final_frames="${FINAL_FRAMES:-30551}"

picture_file="${PICTURE_FILE:-${project_dir}/renders/v10_candidate_14m_clean/PICTURE_MASTER_V10_1080P_CLEAN.mp4}"
voice_mix="${AUDIO_FILE:-${project_dir}/audio/mix/FULL_MIX_V10_CONTENT_48K.wav}"
credit_file="${CREDIT_FILE:-${project_dir}/CREDIT_TPHCM_OH_YEAH_V4.mp4}"
srt_file="${SRT_FILE:-${project_dir}/qa/v9/05_subtitles_v9.srt}"
subtitle_dir="${SUBTITLE_DIR:-${project_dir}/renders/v10_final/subtitles}"
subtitle_file="${SUBTITLE_FILE:-${subtitle_dir}/SUBTITLE_ALPHA_V10_CONTENT_1080P.mov}"
output_file="${OUTPUT_FILE:-${project_dir}/renders/v10_final/FINAL_FEENBERG_DOCUMENTARY_V10_candidate.mp4}"

for input_file in "${picture_file}" "${voice_mix}" "${credit_file}" "${srt_file}"; do
  [[ -f "${input_file}" ]] || { print -u2 "Missing V10 final input: ${input_file}"; exit 1; }
done

mkdir -p "${subtitle_dir}" "${output_file:h}"

/opt/homebrew/bin/python3.13 "${script_dir}/build_subtitle_overlay.py" \
  --srt "${srt_file}" \
  --output "${subtitle_file}" \
  --work-dir "${subtitle_dir}/frames" \
  --duration "${content_duration}"

# Subtitles exist only on the content picture.  The last cue ends before the
# 0.8-second bridge, so no caption leaks onto the standalone credit artifact.
# Video and both music masters crossfade in the same interval.
ffmpeg -hide_banner -loglevel error -y \
  -i "${picture_file}" \
  -i "${subtitle_file}" \
  -i "${voice_mix}" \
  -i "${credit_file}" \
  -filter_complex \
    "[0:v]trim=duration=${content_duration},setpts=PTS-STARTPTS,settb=AVTB[base];\
     [1:v]trim=duration=${content_duration},setpts=PTS-STARTPTS,settb=AVTB[sub];\
     [base][sub]overlay=0:0:format=auto:eof_action=pass,trim=duration=${content_duration},fps=30,setsar=1,format=yuv420p,settb=AVTB[contentv];\
     [3:v]trim=duration=${credit_duration},setpts=PTS-STARTPTS,fps=30,scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p,settb=AVTB[creditv];\
     [contentv][creditv]xfade=transition=fade:duration=${crossfade}:offset=${crossfade_offset},trim=duration=${final_duration},setpts=PTS-STARTPTS,fps=30,setsar=1,format=yuv420p[outv];\
     [2:a]aresample=48000,atrim=0:${content_duration},asetpts=PTS-STARTPTS[contenta];\
     [3:a]aresample=48000,atrim=0:${credit_duration},asetpts=PTS-STARTPTS[credita];\
     [contenta][credita]acrossfade=d=${crossfade}:c1=qsin:c2=qsin,atrim=duration=${final_duration},loudnorm=I=-16:TP=-2:LRA=8:linear=true[outa]" \
  -map "[outv]" -map "[outa]" \
  -frames:v "${final_frames}" -t "${final_duration}" \
  -c:v h264_videotoolbox -profile:v high -level:v 4.2 \
  -b:v 20M -maxrate 28M -bufsize 40M -g 60 -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 \
  -bsf:v "h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1" \
  -c:a aac -profile:a aac_low -b:a 320k -ar 48000 -ac 2 \
  -movflags +faststart -tag:v avc1 \
  "${output_file}"

print "V10 final candidate: ${output_file}"
