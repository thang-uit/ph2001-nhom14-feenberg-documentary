#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
project_dir="${script_dir:h}"
source_file="${project_dir}/01_narration.txt"
voice_dir="${project_dir}/audio/vo"
work_dir="${voice_dir}/draft_sections"
manifest_file="${voice_dir}/narration_sections.json"
voice_name="${VOICE_NAME:-Linh}"
initial_rate="${VOICE_RATE:-210}"
fill_ratio="${VOICE_FILL_RATIO:-0.985}"

command -v python3 >/dev/null
command -v say >/dev/null
command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null

mkdir -p "${voice_dir}" "${work_dir}"

python3 "${script_dir}/extract_narration.py" \
  --source "${source_file}" \
  --output-dir "${voice_dir}"

voice_record="$(say -v '?' | awk -v requested="${voice_name}" '$1 == requested {print; exit}')"
if [[ -z "${voice_record}" ]]; then
  print -u2 "Voice '${voice_name}' is not installed."
  exit 1
fi

rm -f -- "${work_dir}"/section_*.aiff(N) "${work_dir}"/section_*.wav(N)

python3 - "${manifest_file}" "${work_dir}" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
work_dir = Path(sys.argv[2])
for section in manifest["sections"]:
    path = work_dir / f"section_{section['index']:02d}.txt"
    path.write_text(section["say_text"] + "\n", encoding="utf-8")
PY

report_tmp="${work_dir}/timing_report.tsv"
print 'SECTION\tSTART\tEND\tTARGET_SEC\tRATE_WPM\tRAW_SEC\tATEMPO\tVOICE_SEC\tPADDED_SEC\tWORDS\tTITLE' > "${report_tmp}"

section_count="$(python3 -c 'import json,sys; print(len(json.load(open(sys.argv[1], encoding="utf-8"))["sections"]))' "${manifest_file}")"

integer=1
while (( integer <= section_count )); do
  index="$(printf '%02d' "${integer}")"
  section_text="${work_dir}/section_${index}.txt"
  raw_audio="${work_dir}/section_${index}.aiff"
  padded_audio="${work_dir}/section_${index}.wav"

  read -r start_time end_time target_seconds word_count title <<< "$(python3 - "${manifest_file}" "${integer}" <<'PY'
import json
import shlex
import sys

section = json.load(open(sys.argv[1], encoding="utf-8"))["sections"][int(sys.argv[2]) - 1]
values = [
    section["start_time"],
    section["end_time"],
    str(section["target_duration_seconds"]),
    str(section["word_count"]),
    section["title"],
]
print(" ".join(shlex.quote(value) for value in values))
PY
)"

  rate="${initial_rate}"
  target_voice_seconds="$(python3 -c 'import sys; print(float(sys.argv[1]) * float(sys.argv[2]))' "${target_seconds}" "${fill_ratio}")"
  attempt=1
  while (( attempt <= 6 )); do
    say -v "${voice_name}" -r "${rate}" -f "${section_text}" -o "${raw_audio}"
    raw_seconds="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "${raw_audio}")"
    next_rate="$(python3 - "${rate}" "${raw_seconds}" "${target_voice_seconds}" <<'PY'
import sys
rate = float(sys.argv[1])
actual = float(sys.argv[2])
target = float(sys.argv[3])
next_rate = max(55.0, min(280.0, rate * actual / target))
print(round(next_rate))
PY
)"
    delta="$(python3 -c 'import sys; print(abs(float(sys.argv[1])-float(sys.argv[2])))' "${raw_seconds}" "${target_voice_seconds}")"
    close_enough="$(python3 -c 'import sys; print(1 if float(sys.argv[1]) <= 1.5 else 0)' "${delta}")"
    fits_slot="$(python3 -c 'import sys; print(1 if float(sys.argv[1]) < float(sys.argv[2]) else 0)' "${raw_seconds}" "${target_seconds}")"
    if [[ "${close_enough}" == "1" && "${fits_slot}" == "1" ]]; then
      break
    fi
    if [[ "${next_rate}" == "${rate}" ]]; then
      if [[ "${fits_slot}" == "1" ]]; then
        break
      fi
      next_rate="$(( rate + 5 ))"
    fi
    rate="${next_rate}"
    (( attempt += 1 ))
  done

  raw_seconds="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "${raw_audio}")"
  tempo="$(python3 -c 'import sys; print(f"{float(sys.argv[1]) / float(sys.argv[2]):.8f}")' "${raw_seconds}" "${target_voice_seconds}")"
  tempo_valid="$(python3 -c 'import sys; value=float(sys.argv[1]); print(1 if 0.5 <= value <= 2.0 else 0)' "${tempo}")"
  if [[ "${tempo_valid}" != "1" ]]; then
    print -u2 "Section ${index} requires unsupported atempo ${tempo}."
    exit 1
  fi

  ffmpeg -hide_banner -loglevel error -y -i "${raw_audio}" \
    -af "atempo=${tempo},aresample=48000,apad=whole_dur=${target_seconds},atrim=0:${target_seconds}" \
    -ar 48000 -ac 2 -c:a pcm_s24le "${padded_audio}"
  padded_seconds="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "${padded_audio}")"
  voice_seconds="$(python3 -c 'import sys; print(f"{float(sys.argv[1]) / float(sys.argv[2]):.6f}")' "${raw_seconds}" "${tempo}")"
  print "${index}\t${start_time}\t${end_time}\t${target_seconds}\t${rate}\t${raw_seconds}\t${tempo}\t${voice_seconds}\t${padded_seconds}\t${word_count}\t${title}" >> "${report_tmp}"
  (( integer += 1 ))
done

concat_file="${work_dir}/concat.txt"
: > "${concat_file}"
integer=1
while (( integer <= section_count )); do
  index="$(printf '%02d' "${integer}")"
  escaped_path="${work_dir}/section_${index}.wav"
  print "file '${escaped_path}'" >> "${concat_file}"
  (( integer += 1 ))
done

timeline_raw="${voice_dir}/VO_DRAFT_TIMELINE_RAW_48K.wav"
timeline_final="${voice_dir}/VO_DRAFT_LINH_48K.wav"
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "${concat_file}" \
  -ar 48000 -ac 2 -c:a pcm_s24le "${timeline_raw}"

ffmpeg -hide_banner -loglevel error -y -i "${timeline_raw}" \
  -af "loudnorm=I=-20:TP=-3:LRA=7" \
  -ar 48000 -ac 2 -c:a pcm_s24le "${timeline_final}"

cp "${report_tmp}" "${voice_dir}/voice_draft_timing.tsv"
ffprobe -v error -show_entries format=duration:stream=codec_name,sample_rate,channels \
  -of json "${timeline_final}" > "${voice_dir}/voice_draft_ffprobe.json"

print "Voice draft created: ${timeline_final}"
print "Timing report: ${voice_dir}/voice_draft_timing.tsv"
