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

picture_file="${PICTURE_FILE:-${project_dir}/renders/v11_final_r6/PICTURE_MASTER_V11_R6_1080P.mp4}"
content_mix="${AUDIO_FILE:-${project_dir}/audio/mix/FULL_MIX_V10_CONTENT_48K.wav}"
credit_file="${CREDIT_FILE:-${project_dir}/CREDIT_TPHCM_OH_YEAH_V4.mp4}"
srt_file="${SRT_FILE:-${project_dir}/qa/v9/05_subtitles_v9.srt}"
subtitle_dir="${SUBTITLE_DIR:-${project_dir}/renders/v11_final_r6/subtitles}"
subtitle_file="${SUBTITLE_FILE:-${subtitle_dir}/SUBTITLE_ALPHA_V11_R6_CONTENT_1080P.mov}"
output_file="${OUTPUT_FILE:-${project_dir}/renders/v11_final_r6/FINAL_FEENBERG_DOCUMENTARY_V11_R6_rebuild_candidate.mp4}"

for input_file in "${picture_file}" "${content_mix}" "${credit_file}" "${srt_file}"; do
  [[ -f "${input_file}" ]] || { print -u2 "Missing V11 final input: ${input_file}"; exit 1; }
done

mkdir -p "${subtitle_dir}" "${output_file:h}"

if [[ ! -f "${subtitle_file}" || "${REBUILD_SUBTITLES:-0}" == "1" ]]; then
  /opt/homebrew/bin/python3.13 "${script_dir}/build_v11_subtitle_overlay.py" \
    --srt "${srt_file}" \
    --output "${subtitle_file}" \
    --work-dir "${subtitle_dir}/frames" \
    --duration "${content_duration}"
fi

# Caption only the 965.067-second content master.  Picture and programme
# audio then crossfade together into the rounded-card 54.1-second V4 credit.
# A final transparent loudness pass controls the music overlap at the bridge
# without modifying the locked Vale narration timing.
ffmpeg -hide_banner -loglevel error -y \
  -i "${picture_file}" \
  -i "${subtitle_file}" \
  -i "${content_mix}" \
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
  -b:v 22M -maxrate 30M -bufsize 44M -g 60 -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 \
  -bsf:v "h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1" \
  -c:a aac -profile:a aac_low -b:a 320k -ar 48000 -ac 2 \
  -movflags +faststart -tag:v avc1 \
  "${output_file}"

print "V11 R6 final candidate: ${output_file}"
