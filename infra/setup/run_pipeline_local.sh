#!/bin/bash
#
# Interactive/local counterpart to run_pipeline_gantry.sh.
#
# Runs infra/pipeline.py directly in the current shell for each environment
# matched by APP_FILTER (or all envs if unset). No gantry, no beaker, no
# per-job container setup — assumes the repo is already set up locally
# (uv-managed venv + `claude login` or ANTHROPIC_API_KEY).
#
# Usage:
#   bash infra/setup/run_pipeline_local.sh
#   APP_FILTER=wikipedia-article-browsing bash infra/setup/run_pipeline_local.sh
#   MODEL=claude WORKERS=4 HARDENING_ROUNDS=2 \
#     APP_FILTER=arxiv-paper-search bash infra/setup/run_pipeline_local.sh
#
# Environment variables (all optional):
#   MANIFEST          Path to env_manifest.jsonl (default: infra/env_manifest.jsonl)
#   APP_FILTER        Comma- or newline-separated env_ids to include (default: all)
#   REPO_ROOT         Absolute path to the webarena-infinity repo
#                     (default: /weka/oe-training-default/zixianm/webarena-infinity)
#   MODEL             Eval agent model (default: gemini-pro)
#   WORKERS           Parallel eval workers (default: 8)
#   REPETITIONS       Eval repetitions (default: 3)
#   MAX_ITERATIONS    Max eval-audit loops (default: 3)
#   HARDENING_ROUNDS  Hardening rounds (default: 3)
#   TASKS_PER_ROUND   New tasks per hardening round (default: 20)
#   RERUN_FROM        If set, passed through to pipeline.py --rerun-from
#   DRY_RUN           If "1", print the pipeline command(s) without running

set -euo pipefail

# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────

REPO_ROOT="${REPO_ROOT:-/weka/oe-training-default/zixianm/webarena-infinity}"
MANIFEST="${MANIFEST:-infra/env_manifest.jsonl}"
APP_FILTER="${APP_FILTER:-}"

MODEL="${MODEL:-gemini-pro}"
WORKERS="${WORKERS:-8}"
REPETITIONS="${REPETITIONS:-3}"
MAX_ITERATIONS="${MAX_ITERATIONS:-3}"
HARDENING_ROUNDS="${HARDENING_ROUNDS:-3}"
TASKS_PER_ROUND="${TASKS_PER_ROUND:-20}"
RERUN_FROM="${RERUN_FROM:-}"
DRY_RUN="${DRY_RUN:-0}"

cd "$REPO_ROOT"

if [ ! -f "$MANIFEST" ]; then
  echo "ERROR: Manifest not found: $MANIFEST (cwd=$REPO_ROOT)"
  exit 1
fi

# Ensure ~/.local/bin (where `claude` lives) is on PATH. When invoked via
# `sudo -u <user>`, sudo's secure_path strips non-standard dirs even with -E,
# so we re-add it here.
if [ -d "$HOME/.local/bin" ]; then
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
fi

# ──────────────────────────────────────────────────────────────────────
# Prereq checks
# ──────────────────────────────────────────────────────────────────────

if ! command -v claude >/dev/null 2>&1; then
  echo "ERROR: 'claude' CLI not found on PATH."
  echo "       Install @anthropic-ai/claude-code and run 'claude login'."
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: 'uv' not found on PATH. Install uv (https://astral.sh/uv)."
  exit 1
fi

# ──────────────────────────────────────────────────────────────────────
# Parse + filter manifest (same logic as run_pipeline_gantry.sh)
# ──────────────────────────────────────────────────────────────────────

ALLOWED=""
if [ -n "$APP_FILTER" ]; then
  ALLOWED=$(echo "$APP_FILTER" | tr ',\n' '  ')
fi

mapfile -t MANIFEST_LINES < <(grep -v '^\s*$' "$MANIFEST")
if [ ${#MANIFEST_LINES[@]} -eq 0 ]; then
  echo "ERROR: Manifest is empty: $MANIFEST"
  exit 1
fi

ENV_IDS=()
DOCS_PATHS=()
for line in "${MANIFEST_LINES[@]}"; do
  eid=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['env_id'])")
  docs=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['docs_path'])")

  if [ -n "$ALLOWED" ]; then
    match=0
    for a in $ALLOWED; do
      [ "$a" = "$eid" ] && match=1 && break
    done
    [ $match -eq 0 ] && continue
  fi

  ENV_IDS+=("$eid")
  DOCS_PATHS+=("$docs")
done

if [ ${#ENV_IDS[@]} -eq 0 ]; then
  echo "ERROR: No environments matched (manifest=$MANIFEST, filter='$APP_FILTER')"
  exit 1
fi

# De-duplicate while preserving order
declare -A SEEN
UNIQUE_ENV_IDS=()
UNIQUE_DOCS_PATHS=()
for i in "${!ENV_IDS[@]}"; do
  k="${ENV_IDS[$i]}"
  if [ -z "${SEEN[$k]:-}" ]; then
    SEEN[$k]=1
    UNIQUE_ENV_IDS+=("$k")
    UNIQUE_DOCS_PATHS+=("${DOCS_PATHS[$i]}")
  fi
done
ENV_IDS=("${UNIQUE_ENV_IDS[@]}")
DOCS_PATHS=("${UNIQUE_DOCS_PATHS[@]}")

echo "============================================================"
echo "  WebArena-Infinity pipeline (local / interactive)"
echo "============================================================"
echo "  Repo:               $REPO_ROOT"
echo "  Manifest:           $MANIFEST"
echo "  Filter:             ${APP_FILTER:-<all>}"
echo "  Environments:       ${#ENV_IDS[@]}"
for e in "${ENV_IDS[@]}"; do echo "    - $e"; done
echo "  Model:              $MODEL"
echo "  Workers:            $WORKERS"
echo "  Repetitions:        $REPETITIONS"
echo "  Max iterations:     $MAX_ITERATIONS"
echo "  Hardening rounds:   $HARDENING_ROUNDS"
echo "  Tasks per round:    $TASKS_PER_ROUND"
[ -n "$RERUN_FROM" ] && echo "  Rerun from:         $RERUN_FROM"
echo "  Dry run:            $DRY_RUN"
echo "============================================================"

# ──────────────────────────────────────────────────────────────────────
# Per-env local execution
# ──────────────────────────────────────────────────────────────────────

run_one() {
  local env_id="$1"
  local docs_path="$2"

  local cmd=(
    uv run python infra/pipeline.py
    --app-name "$env_id"
    --docs-path "$docs_path"
    --model "$MODEL"
    --workers "$WORKERS"
    --repetitions "$REPETITIONS"
    --max-iterations "$MAX_ITERATIONS"
    --hardening-rounds "$HARDENING_ROUNDS"
    --tasks-per-round "$TASKS_PER_ROUND"
    --branch "$env_id"
    --no-push
  )
  if [ -n "$RERUN_FROM" ]; then
    cmd+=(--rerun-from "$RERUN_FROM")
  fi

  echo ""
  echo "── Running pipeline for: $env_id"
  echo "   docs_path=$docs_path"
  echo "   cmd: ${cmd[*]}"

  if [ "$DRY_RUN" = "1" ]; then
    echo "   [DRY RUN] skipping execution"
    return 0
  fi

  "${cmd[@]}"
  echo "✅ Pipeline finished for $env_id"
}

for i in "${!ENV_IDS[@]}"; do
  run_one "${ENV_IDS[$i]}" "${DOCS_PATHS[$i]}"
done

echo ""
echo "============================================================"
echo "  Finished ${#ENV_IDS[@]} pipeline run(s)"
echo "============================================================"
