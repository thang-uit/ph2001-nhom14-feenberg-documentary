#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"
raw_dir="${project_dir}/assets/flow/proof/raw"
overlay_dir="${project_dir}/assets/flow/proof/overlays"
work_dir="${project_dir}/assets/flow/proof/work"
output_file="${OUTPUT_FILE:-${project_dir}/renders/PROOF_OF_STYLE_v01.mp4}"
audio_file="${AUDIO_FILE:-${project_dir}/audio/mix/FULL_MIX_DRAFT_48K.wav}"
subtitle_file="${project_dir}/05_subtitles.srt"
subtitle_overlay="${work_dir}/PROOF_SUBTITLES_ALPHA.mov"
title_overlay="${project_dir}/assets/graphics/S005_title_overlay.png"

command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null

python3 "${script_dir}/build_proof_overlays.py"
python3 "${script_dir}/qa_flow_assets.py" --project-dir "${project_dir}" --scope proof

mkdir -p "${work_dir}" "${output_file:h}" "${project_dir}/qa"
rm -f "${work_dir}"/S00{1,2,3,4,5,6}_normalized.mp4 "${work_dir}/proof.ffconcat"

python3 "${script_dir}/build_subtitle_overlay.py" \
  --srt "${subtitle_file}" \
  --output "${subtitle_overlay}" \
  --work-dir "${work_dir}/subtitles" \
  --start 0 \
  --duration 55

typeset -A basename_by_scene
basename_by_scene=(
  S001 S001_clinic_arrival
  S002 S002_phone_tap
  S003 S003_open_black_box
  S004 S004_design_power_participation
  S005 S005_title_plate
  S006 S006_waiting_chair
)

typeset -A duration_by_scene
duration_by_scene=(S001 7 S002 7 S003 8 S004 10 S005 13 S006 10)

function resolve_clip() {
  local basename="$1"
  local -a matches
  matches=("${raw_dir}"/**/"${basename}".(mp4|mov|mkv|webm)(N))
  if (( ${#matches} != 1 )); then
    print -u2 "Expected exactly one clip named ${basename}, found ${#matches}"
    return 1
  fi
  print -r -- "${matches[1]}"
}

for scene_id in S001 S002 S003 S004 S005 S006; do
  input_file="$(resolve_clip "${basename_by_scene[$scene_id]}")"
  duration="${duration_by_scene[$scene_id]}"
  normalized_file="${work_dir}/${scene_id}_normalized.mp4"
  if [[ "${scene_id}" == "S005" ]]; then
    overlay_file="${title_overlay}"
  else
    overlay_file="${overlay_dir}/${scene_id}_overlay.png"
  fi

  # tpad only covers the title plate when Flow supplies a shorter stable hold.
  # Other scenes must already meet their required duration and are rejected by
  # qa_flow_assets.py before this loop starts.
  if [[ "${scene_id}" == "S005" ]]; then
    pad_filter="tpad=stop_mode=clone:stop_duration=13,"
  else
    pad_filter=""
  fi

  ffmpeg -hide_banner -loglevel error -y \
    -i "${input_file}" -loop 1 -i "${overlay_file}" \
    -filter_complex \
      "[0:v]${pad_filter}trim=duration=${duration},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps=30,setsar=1,format=yuv420p[base];\
       [1:v]scale=1920:1080:flags=lanczos,format=rgba[overlay];\
       [base][overlay]overlay=0:0:format=auto:shortest=1,format=yuv420p[out]" \
    -map "[out]" -an -t "${duration}" -r 30 \
    -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 \
    -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 \
    -movflags +faststart "${normalized_file}"
done

{
  print "ffconcat version 1.0"
  for scene_id in S001 S002 S003 S004 S005 S006; do
    print "file '${work_dir}/${scene_id}_normalized.mp4'"
  done
} > "${work_dir}/proof.ffconcat"

ffmpeg -hide_banner -loglevel error -y \
  -f concat -safe 0 -i "${work_dir}/proof.ffconcat" \
  -i "${audio_file}" \
  -i "${subtitle_overlay}" \
  -filter_complex \
    "[0:v][2:v]overlay=0:0:format=auto:shortest=1,format=yuv420p[video];\
     [1:a]atrim=0:55,asetpts=PTS-STARTPTS[audio]" \
  -map "[video]" -map "[audio]" -t 55 \
  -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 15 \
  -pix_fmt yuv420p -r 30 -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 \
  -c:a aac -b:a 320k -ar 48000 -ac 2 -movflags +faststart \
  "${output_file}"

ffprobe -v error \
  -show_entries format=filename,duration,size,bit_rate:stream=index,codec_name,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,sample_aspect_ratio,field_order,color_range,color_space,color_transfer,color_primaries,sample_rate,channels \
  -of json "${output_file}" > "${project_dir}/qa/proof_of_style_ffprobe.json"

print "Style proof rendered: ${output_file}"
print "Technical probe: ${project_dir}/qa/proof_of_style_ffprobe.json"
