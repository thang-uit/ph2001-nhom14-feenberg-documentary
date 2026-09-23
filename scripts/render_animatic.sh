#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"
slate_dir="${project_dir}/video/animatic_slates"
concat_file="${slate_dir}/animatic.ffconcat"
voice_file="${project_dir}/audio/vo/VO_DRAFT_LINH_48K.wav"
subtitle_file="${project_dir}/05_subtitles.srt"
output_file="${project_dir}/renders/ANIMATIC_TIMING_ONLY.mp4"
probe_file="${project_dir}/qa/animatic_ffprobe.json"

command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null

mkdir -p "${slate_dir}" "${project_dir}/renders" "${project_dir}/qa"

python3 "${script_dir}/build_animatic.py" \
  --storyboard "${project_dir}/02_storyboard.csv" \
  --subtitles "${subtitle_file}" \
  --project-dir "${project_dir}" \
  --output-dir "${slate_dir}"

if [[ ! -f "${voice_file}" ]]; then
  print -u2 "Voice draft missing: ${voice_file}"
  exit 1
fi
if [[ ! -f "${subtitle_file}" ]]; then
  print -u2 "Subtitle file missing: ${subtitle_file}"
  exit 1
fi

ffmpeg -hide_banner -loglevel error -y \
  -f concat -safe 0 -i "${concat_file}" \
  -i "${voice_file}" \
  -vf "scale=in_range=full:out_range=tv:out_color_matrix=bt709,fps=30,format=yuv420p" \
  -af "apad=whole_dur=1160,atrim=0:1160" \
  -t 1160 \
  -c:v libx264 -preset veryfast -crf 24 -profile:v high -level 4.1 \
  -pix_fmt yuv420p -r 30 -g 60 \
  -x264-params "colorprim=bt709:transfer=bt709:colormatrix=bt709:fullrange=off" \
  -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  "${output_file}"

ffprobe -v error \
  -show_entries format=filename,duration,size,bit_rate:stream=index,codec_name,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,sample_aspect_ratio,field_order,color_range,color_space,color_transfer,color_primaries,sample_rate,channels \
  -of json "${output_file}" > "${probe_file}"

print "Animatic rendered: ${output_file}"
print "Technical probe: ${probe_file}"
