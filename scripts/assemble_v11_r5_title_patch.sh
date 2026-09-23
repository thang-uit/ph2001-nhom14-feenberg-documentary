#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"

content_duration="965.066667"
credit_duration="54.100000"
crossfade="0.800000"
crossfade_offset="964.266667"
final_duration="1018.366667"
final_frames="30551"

picture_file="${project_dir}/renders/v11_final_r5/PICTURE_MASTER_V11_R5_1080P.mp4"
subtitle_file="${project_dir}/renders/v11_final_r5/subtitles/SUBTITLE_ALPHA_V11_R5_CONTENT_1080P.mov"
credit_file="${project_dir}/CREDIT_TPHCM_OH_YEAH_V4.mp4"
locked_delivery="${project_dir}/Nhom14_DanChuHoaThietKeVaQuanTriCongNgheTheoFeenberg.mp4"
output_file="${project_dir}/renders/v11_final_r5/FINAL_FEENBERG_DOCUMENTARY_V11_R5_rebuild_candidate.mp4"

for input_file in "${picture_file}" "${subtitle_file}" "${credit_file}" "${locked_delivery}"; do
  [[ -f "${input_file}" ]] || { print -u2 "Missing R5 title-patch input: ${input_file}"; exit 1; }
done

mkdir -p "${output_file:h}"

# R5 changes picture only.  The complete encoded audio stream is copied from
# the locked R4 delivery so voice, music, ambience, credit mix and timing stay
# byte-for-byte unchanged.
ffmpeg -hide_banner -loglevel error -y \
  -i "${picture_file}" \
  -i "${subtitle_file}" \
  -i "${credit_file}" \
  -i "${locked_delivery}" \
  -filter_complex \
    "[0:v]trim=duration=${content_duration},setpts=PTS-STARTPTS,settb=AVTB[base];\
     [1:v]trim=duration=${content_duration},setpts=PTS-STARTPTS,settb=AVTB[sub];\
     [base][sub]overlay=0:0:format=auto:eof_action=pass,trim=duration=${content_duration},fps=30,setsar=1,format=yuv420p,settb=AVTB[contentv];\
     [2:v]trim=duration=${credit_duration},setpts=PTS-STARTPTS,fps=30,scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p,settb=AVTB[creditv];\
     [contentv][creditv]xfade=transition=fade:duration=${crossfade}:offset=${crossfade_offset},trim=duration=${final_duration},setpts=PTS-STARTPTS,fps=30,setsar=1,format=yuv420p[outv]" \
  -map "[outv]" -map 3:a:0 \
  -frames:v "${final_frames}" \
  -c:v h264_videotoolbox -profile:v high -level:v 4.2 \
  -b:v 22M -maxrate 30M -bufsize 44M -g 60 -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 \
  -bsf:v "h264_metadata=video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1" \
  -c:a copy -movflags +faststart -tag:v avc1 \
  "${output_file}"

print "V11 R5 title-patch candidate: ${output_file}"
