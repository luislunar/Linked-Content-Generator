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

# Claude Code CLI in headless mode. --dangerously-skip-permissions is safe here because .claude/settings.json
# already restricts the tool surface to the scripts we authored.
claude -p "$PROMPT" \
  --model claude-opus-4-7 \
  --dangerously-skip-permissions \
  2>&1 | tee "logs/run-$(date +%Y-%m-%d)-$MODE.log"
