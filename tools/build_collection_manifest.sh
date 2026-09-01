#!/bin/zsh
set -euo pipefail

script_dir="${0:A:h}"
wave_dir="${script_dir:h}"
manifest_tmp="$(mktemp)"

mkdir -p "$wave_dir/outputs" "$wave_dir/capture_metadata" "$wave_dir/ratings" "$wave_dir/analysis"

printf '%s\n' 'run_id,scenario_id,variant,product,repetition,prompt_path,prompt_sha256,status,attempts,started_at,completed_at,output_path,capture_metadata_path,failure_reason' > "$manifest_tmp"

for prompt_path in "$wave_dir"/prompts/*.txt; do
  prompt_name="${prompt_path:t:r}"
  scenario_id="${prompt_name%%__*}"
  variant="${prompt_name##*__}"
  prompt_sha256="$(shasum -a 256 "$prompt_path" | awk '{print $1}')"
  relative_prompt_path="prompts/${prompt_path:t}"

  for product in chatgpt claude copilot gemini; do
    for repetition in 1 2; do
      run_id="w4__${scenario_id}__${variant}__${product}__r${repetition}"
      output_path="outputs/${run_id}.txt"
      capture_metadata_path="capture_metadata/${run_id}.json"
      printf '%s\n' "${run_id},${scenario_id},${variant},${product},${repetition},${relative_prompt_path},${prompt_sha256},planned,0,,,${output_path},${capture_metadata_path}," >> "$manifest_tmp"
    done
  done
done

mv "$manifest_tmp" "$wave_dir/collection_manifest.csv"
