#!/usr/bin/env bash
# overlay-text.sh — burn Gotham/neon-green overlay onto a raw scroll recording.
#
# Usage: ./scripts/overlay-text.sh <input.webm> <output.mp4> <hook_main> [hook_sub]
#
# Requires: ffmpeg with libass + libfreetype, and the font files in assets/fonts/.

set -euo pipefail

# Prefer Homebrew's ffmpeg-full (has libass/libfreetype/fontconfig for subtitles + drawtext).
# The default ffmpeg formula on macOS is built minimal and lacks the subtitles filter.
if [ -x /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg ]; then
  FFMPEG=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
else
  FFMPEG=ffmpeg
fi

INPUT=$1
OUTPUT=$2
HOOK_MAIN=${3:?"hook_main required"}
HOOK_SUB=${4:-""}

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$REPO_ROOT/assets/overlay-template.ass"
# Stage everything (input, subtitles, fonts) into a path with no spaces/colons so
# ffmpeg's subtitles= filter doesn't choke parsing the path.
WORK=$(mktemp -d -t overlay)
trap 'rm -rf "$WORK"' EXIT

cp -R "$REPO_ROOT/assets/fonts" "$WORK/fonts"
cp "$INPUT" "$WORK/input.webm"

# Inputs may contain ASS control sequences (\N for newline, {...} for inline
# overrides); those pass through to libass unchanged. Only real unescaped newlines
# need conversion — we don't expect those from the CLI so no transform is needed.
#
# Combine main + sub into a single dialogue line so both render inside ONE opaque
# green box. The inline override {\fnMontserrat Medium\fs30\b0} switches the sub
# portion to Montserrat Medium 30pt non-bold.
if [ -n "$HOOK_SUB" ]; then
  COMBINED="${HOOK_MAIN}\N{\fnMontserrat Medium\fs30\b0}${HOOK_SUB}"
else
  COMBINED="$HOOK_MAIN"
fi

# Build overlay.ass in Python to sidestep sed's backslash-escaping rules —
# the replacement text contains \N and \f... sequences that must reach libass verbatim.
python3 - "$TEMPLATE" "$WORK/overlay.ass" "$COMBINED" <<'PY'
import sys
tpl_path, out_path, combined = sys.argv[1], sys.argv[2], sys.argv[3]
tpl = open(tpl_path).read()
open(out_path, "w").write(tpl.replace("{{HOOK_COMBINED}}", combined))
PY

# Run ffmpeg from $WORK so the filter's relative paths contain no spaces/colons.
# -sseof -5.3 grabs the last 5.3s — the scripted down(3s)+up(2s)+200ms tail —
# from Playwright's recording, trimming off page load + lazy-load warm-up.
( cd "$WORK" && "$FFMPEG" -y -sseof -5.3 -i input.webm \
  -vf "subtitles=overlay.ass:fontsdir=fonts" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -movflags +faststart \
  -an \
  output.mp4 )

mv "$WORK/output.mp4" "$OUTPUT"

echo "$OUTPUT"
