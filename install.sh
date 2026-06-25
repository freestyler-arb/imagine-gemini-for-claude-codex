#!/usr/bin/env bash
# install.sh — install the `gemini` wrapper + the Gemini skills for Claude Code and Codex.
#
#   ./install.sh                              # wrapper -> ~/.local/bin, skills -> Claude + Codex
#   BIN_DIR=~/bin ./install.sh                # override the wrapper location
#   SKILLS_DIRS="$HOME/.claude/skills" ./install.sh   # install skills to specific dir(s) only
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"

# Skill targets: Claude Code (~/.claude/skills) and Codex (~/.agents/skills).
# Same SKILL.md works in both. Override with SKILLS_DIRS="dir1 dir2".
SKILLS_DIRS="${SKILLS_DIRS:-$HOME/.claude/skills $HOME/.agents/skills}"

echo "==> Installing wrapper -> $BIN_DIR/gemini"
mkdir -p "$BIN_DIR"
install -m 0755 "$REPO_DIR/bin/gemini" "$BIN_DIR/gemini"

for dir in $SKILLS_DIRS; do
  dir="${dir/#\~/$HOME}"          # expand a leading ~ that survived quoting
  echo "==> Installing skills  -> $dir"
  mkdir -p "$dir"
  for skill in "$REPO_DIR"/skills/*/; do
    name="$(basename "$skill")"
    rm -rf "${dir:?}/$name"
    cp -R "$skill" "$dir/$name"
    echo "    + $name"
  done
done

echo
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    echo "NOTE: $BIN_DIR is not on your PATH. Add it so 'gemini' is found:"
    echo "      echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.zshrc   # or ~/.bashrc"
    echo "      exec \$SHELL"
    echo ;;
esac
echo "Done. Next steps:"
echo "  1. Install the Antigravity CLI:  brew install --cask antigravity-cli"
echo "  2. Log in once (interactive):     agy        # pick your Google AI Pro account"
echo "  3. Smoke test:                    gemini 'reply with one word: ok'"
echo "  4. In Claude Code / Codex the skills activate automatically when your request"
echo "     matches their description (e.g. 'ask Gemini Pro to ...')."
