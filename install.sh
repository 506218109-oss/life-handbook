#!/usr/bin/env bash
# Install life-handbook as a ZCode user skill and fetch the guide text.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.agents/skills/life-handbook"
mkdir -p "$DEST"
cp -R "$SRC/SKILL.md" "$SRC/scripts" "$DEST/"
python3 "$DEST/scripts/fetch_guide.py"
echo ""
echo "Installed at: $DEST"
echo "Restart your ZCode session, then ask it a life question, e.g.: 体检中心推销全身PET-CT，做吗？"
