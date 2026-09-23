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

picture_file="${project_dir}/renders/v11_final_r6/PICTURE_MASTER_V11_R6_1080P.mp4"
subtitle_file="${project_dir}/renders/v11_final_r6/subtitles/SUBTITLE_ALPHA_V11_R6_CONTENT_1080P.mov"
credit_file="${project_dir}/CREDIT_TPHCM_OH_YEAH_V4.mp4"
locked_r5="${project_dir}/renders/archive_v11/FINAL_FEENBERG_DOCUMENTARY_V11_R5_LOCKED.mp4"
staging_file="${project_dir}/renders/v11_final_r6/FINAL_FEENBERG_DOCUMENTARY_V11_R6_candidate.mp4"
output_file="${project_dir}/renders/v11_final_r6/FINAL_FEENBERG_DOCUMENTARY_V11_R6_candidate_audio_exact.mp4"

for input_file in "${picture_file}" "${subtitle_file}" "${credit_file}" "${locked_r5}"; do
  [[ -f "${input_file}" ]] || { print -u2 "Missing R6 source-card patch input: ${input_file}"; exit 1; }
done

mkdir -p "${output_file:h}"

# R6 changes only the nine source-card images.  Copy the complete R5 encoded
# audio stream so voice, music, ambience, credit audio and timing are exactly
# preserved rather than merely recreated from the same source files.
ffmpeg -hide_banner -loglevel error -y \
  -i "${picture_file}" \
  -i "${subtitle_file}" \
  -i "${credit_file}" \
  -i "${locked_r5}" \
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
  "${staging_file}"

# The first mux can truncate a few trailing AAC packets at the video boundary.
# Remux the locked R5 audio once more so R6 keeps the complete, bit-identical
# 47,736-packet programme audio while using only the newly rendered R6 video.
ffmpeg -hide_banner -loglevel error -y \
  -i "${staging_file}" \
  -i "${locked_r5}" \
  -map 0:v:0 -map 1:a:0 \
  -c copy -movflags +faststart \
  "${output_file}"

locked_audio_packets="$(ffprobe -v error -select_streams a:0 -count_packets -show_entries stream=nb_read_packets -of default=nw=1:nk=1 "${locked_r5}")"
output_audio_packets="$(ffprobe -v error -select_streams a:0 -count_packets -show_entries stream=nb_read_packets -of default=nw=1:nk=1 "${output_file}")"
[[ "${output_audio_packets}" == "${locked_audio_packets}" ]] || {
  print -u2 "R6 audio packet mismatch: ${output_audio_packets} != ${locked_audio_packets}"
  exit 1
}

print "V11 R6 source-card patch candidate with exact locked audio: ${output_file}"
