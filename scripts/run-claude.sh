#!/usr/bin/env bash
# run-claude.sh — invoke Claude Code in non-interactive mode with the right command prompt.
#
# Usage:
#   ./scripts/run-claude.sh daily      # runs .claude/commands/daily-magnet.md
#   ./scripts/run-claude.sh weekly     # runs .claude/commands/weekly-research.md
#
# Env required: ANTHROPIC_API_KEY (plus Notion/Blotato envs consumed by the scripts the agent calls).

set -euo pipefail

MODE=${1:?"usage: run-claude.sh daily|weekly"}

case "$MODE" in
  daily)  PROMPT_FILE=".claude/commands/daily-magnet.md" ;;
  weekly) PROMPT_FILE=".claude/commands/weekly-research.md" ;;
  *) echo "unknown mode: $MODE" >&2; exit 2 ;;
esac

# Strip the YAML frontmatter before feeding the body as the prompt.
PROMPT=$(awk 'BEGIN{skip=0} /^---$/{skip=!skip; next} skip==0{print}' "$PROMPT_FILE")

mkdir -p logs

# claude-sonnet-4-6 fits inside the 10k TPM tier-1 limit. To use opus-4-7,
# bump the Anthropic API tier and change MODEL below.
MODEL="${CLAUDE_MODEL:-claude-sonnet-4-6}"

claude -p "$PROMPT" \
  --model "$MODEL" \
  --dangerously-skip-permissions \
  2>&1 | tee "logs/run-$(date +%Y-%m-%d)-$MODE.log"
