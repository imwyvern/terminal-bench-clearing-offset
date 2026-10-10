#!/bin/bash
# Trial commands for this take-home.
# Secrets stay in the environment. This script never writes a key to disk.
#
# Harbor pin used while this repo was checked (terminal-bench main, 2026-10-10):
#   uv tool install "harbor==0.23.1.dev202609170426"
#
# Codex talks to an OpenAI-compatible Responses endpoint. The provider block is
# scripts/codex.config.toml (same text as ~/.codex/config.toml). Harbor does not
# read ~/.codex/config.toml on its own. --ak config=<path> is what loads it.
# Leave OPENAI_BASE_URL unset: Harbor copies that variable onto the top-level
# openai_base_url key and that is the built-in OpenAI provider, not this one.
# Leave CODEX_FORCE_AUTH_JSON unset: that switch requires a ChatGPT auth.json.
#
# DeepSeek uses Harbor's provider table (harbor/agents/model_connection.py):
#   provider deepseek, env DEEPSEEK_API_KEY, default base https://api.deepseek.com
# This Harbor pin has no agent named deepseek. terminus-2 is the agent that
# calls that provider and accepts reasoning_effort=max. The live API model id
# for V4.1 Flash is deepseek-flash, so the Harbor model string is
# deepseek/deepseek-flash. LiteLLM in this pin maps any reasoning_effort other
# than "none" to DeepSeek thinking enabled/disabled and does not forward the
# word "max". The job config still records reasoning_effort=max.

set -euo pipefail

TASK="tasks/clearing-offset"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CODEX_CONFIG="${ROOT}/scripts/codex.config.toml"
cd "$ROOT"

usage() {
  cat <<'EOF'
Usage: scripts/run-trials.sh <oracle|nop|codex-run|codex-cheat|deepseek-run|deepseek-cheat|parse>

  oracle           harbor oracle agent
  nop              harbor nop agent
  codex-run        codex, gpt-6.1-sol, reasoning_effort=xhigh, 3 trials
  codex-cheat      same, 1 trial, hack prompt prepended
  deepseek-run     terminus-2, deepseek/deepseek-flash, reasoning_effort=max, 3 trials
  deepseek-cheat   same, 1 trial, hack prompt prepended
  parse            --print-config and --dry-run for the four trial commands.
                   Does not call a model and does not need API keys.

Codex needs APIKEYCLAW_API_KEY in the environment.
DeepSeek needs DEEPSEEK_API_KEY in the environment (the Harbor process reads it;
terminus-2 calls LiteLLM on the host).
EOF
}

HACK_URL="https://raw.githubusercontent.com/harbor-framework/terminal-bench/main/docs/prompts/hack-trial-prompt.md"

fetch_hack_prompt() {
  local dest="${TMPDIR:-/tmp}/tb-hack-trial-prompt.md"
  curl --fail --silent --show-error --location "$HACK_URL" --output "$dest"
  printf '%s' "$dest"
}

run_harbor() {
  harbor run -p "$TASK" --env docker --yes "$@"
}

require_codex_key() {
  : "${APIKEYCLAW_API_KEY:?set APIKEYCLAW_API_KEY}"
}

require_deepseek_key() {
  : "${DEEPSEEK_API_KEY:?set DEEPSEEK_API_KEY}"
}

codex_args() {
  CODEX_ARGS=(
    --agent codex
    --model openai/gpt-6.1-sol
    --ak "config=${CODEX_CONFIG}"
    --ak reasoning_effort=xhigh
    --ae "APIKEYCLAW_API_KEY=${APIKEYCLAW_API_KEY:-}"
  )
}

deepseek_args() {
  DEEPSEEK_ARGS=(
    --agent terminus-2
    --model deepseek/deepseek-flash
    --ak reasoning_effort=max
    --ae "DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-}"
  )
}

mode="${1:-}"
case "$mode" in
  oracle)
    run_harbor --agent oracle
    ;;
  nop)
    run_harbor --agent nop
    ;;
  codex-run)
    require_codex_key
    codex_args
    run_harbor "${CODEX_ARGS[@]}" -k 3
    ;;
  codex-cheat)
    require_codex_key
    prompt="$(fetch_hack_prompt)"
    codex_args
    run_harbor "${CODEX_ARGS[@]}" -k 1 --extra-instruction-path "$prompt"
    ;;
  deepseek-run)
    require_deepseek_key
    deepseek_args
    run_harbor "${DEEPSEEK_ARGS[@]}" -k 3
    ;;
  deepseek-cheat)
    require_deepseek_key
    prompt="$(fetch_hack_prompt)"
    deepseek_args
    run_harbor "${DEEPSEEK_ARGS[@]}" -k 1 --extra-instruction-path "$prompt"
    ;;
  parse)
    # Config parse and local dry-run only. Empty key placeholders are enough
    # for Harbor to accept the flags; nothing is sent to a model.
    codex_args
    deepseek_args
    echo "=== print-config codex ==="
    run_harbor "${CODEX_ARGS[@]}" -k 3 --print-config
    echo "=== print-config deepseek ==="
    run_harbor "${DEEPSEEK_ARGS[@]}" -k 3 --print-config
    echo "=== dry-run codex ==="
    run_harbor "${CODEX_ARGS[@]}" -k 3 --dry-run
    echo "=== dry-run deepseek ==="
    run_harbor "${DEEPSEEK_ARGS[@]}" -k 3 --dry-run
    prompt="$(fetch_hack_prompt)"
    echo "=== dry-run codex cheat ==="
    run_harbor "${CODEX_ARGS[@]}" -k 1 --extra-instruction-path "$prompt" --dry-run
    echo "=== dry-run deepseek cheat ==="
    run_harbor "${DEEPSEEK_ARGS[@]}" -k 1 --extra-instruction-path "$prompt" --dry-run
    ;;
  *)
    usage
    exit 2
    ;;
esac
