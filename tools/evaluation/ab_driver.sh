#!/usr/bin/env bash
# A/B pass-rate protocol: no-skill control vs bi candidate-29, interleaved order.
# deepseek-flash, thinking max, 400k native compaction, 4h cap per run.
set -uo pipefail
cd "$(dirname "$0")/../.."
EVAL=/Users/zijie/workspace/ByIssue-evaluation
CASE_BI=$EVAL/snapshots/v2-delivery-input-v5/tools/evaluation/cases/byspace-schedules
CASE_NOBI=$EVAL/snapshots/v2-delivery-input-v5-nobi/tools/evaluation/cases/byspace-schedules
SOURCE=$EVAL/snapshots/v2-delivery-candidate-29
MODEL=bytetrueapi/deepseek/deepseek-flash

for i in 01 02 03; do
  echo "=== ab-nobi-$i $(date) ==="
  python3 tools/evaluation/run_repository.py \
    --run "$EVAL/runs/ab-nobi-$i" --no-skill \
    --case "$CASE_NOBI" --model "$MODEL" --thinking max \
    --compact-at 400000 --timeout 14400
  echo "=== ab-bi-$i $(date) ==="
  python3 tools/evaluation/run_repository.py \
    --run "$EVAL/runs/ab-bi-$i" --source "$SOURCE" \
    --case "$CASE_BI" --model "$MODEL" --thinking max \
    --compact-at 400000 --timeout 14400
done
echo "=== all six runs finished $(date) ==="
