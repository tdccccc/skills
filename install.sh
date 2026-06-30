#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
DEST_OVERRIDE=""
LINK_MODE=0
FORCE=1
DRY_RUN=0

usage() {
  cat <<'USAGE'
Usage: install.sh [options]

Install root-level skills from this repository into Claude Code.
Each skill may declare an `install-targets:` field in its SKILL.md frontmatter
(claude, codex, or both); skills that exclude claude are skipped.
A skill without the field defaults to both.

Options:
  --dest DIR       Install into DIR instead of the default skills dir
  --link           Symlink directories instead of copying them
  --no-force       Skip skills that already exist instead of replacing them
  --force          Replace existing installed directories (default)
  --dry-run        Print actions without changing files
  -h, --help       Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      if [[ $# -lt 2 ]]; then echo "error: --dest requires a directory" >&2; exit 2; fi
      DEST_OVERRIDE="$2"
      shift 2
      ;;
    --link)
      LINK_MODE=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --no-force)
      FORCE=0
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '+'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

# Read the `install-targets` field from a skill's SKILL.md frontmatter.
skill_targets() {
  local skill_dir="$1"
  local skill_file="$skill_dir/SKILL.md"
  local line=""
  if [[ -f "$skill_file" ]]; then
    line="$(awk '
      NR==1 && $0=="---" { in_fm=1; next }
      in_fm && $0=="---" { exit }
      in_fm && tolower($0) ~ /^install-targets[[:space:]]*:/ {
        sub(/^[^:]*:[[:space:]]*/, ""); print; exit
      }
    ' "$skill_file")"
  fi
  echo "${line:-both}"
}

skill_wants_claude() {
  local skill_dir="$1"
  local token
  for token in $(skill_targets "$skill_dir"); do
    case "$token" in
      both|claude) return 0 ;;
    esac
  done
  return 1
}

install_dir() {
  local dest_dir="$1" src="$2" name dest
  name="$(basename "$src")"
  dest="$dest_dir/$name"
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$FORCE" -eq 1 ]]; then
      echo "Replacing $name at $dest"
      run rm -rf "$dest"
    else
      echo "Skipping $name: $dest already exists (omit --no-force to replace)"
      return 0
    fi
  fi
  if [[ "$LINK_MODE" -eq 1 ]]; then
    echo "Linking $name -> $dest"
    run ln -s "$src" "$dest"
  else
    echo "Installing $name -> $dest"
    run cp -R "$src" "$dest"
  fi
}

skill_dirs=()
for skill_file in "$ROOT_DIR"/*/SKILL.md; do
  [[ -f "$skill_file" ]] || continue
  skill_dirs+=("$(dirname "$skill_file")")
done

if [[ "${#skill_dirs[@]}" -eq 0 ]]; then
  echo "error: no root-level skills found under $ROOT_DIR" >&2
  exit 1
fi

echo "Installing skills from $ROOT_DIR"
dest_dir="${DEST_OVERRIDE:-$DEFAULT_CLAUDE_CONFIG_DIR/skills}"
echo "Destination: $dest_dir"
run mkdir -p "$dest_dir"

for src in "${skill_dirs[@]}"; do
  if skill_wants_claude "$src"; then
    install_dir "$dest_dir" "$src"
  else
    echo "Skipping $(basename "$src"): install-targets excludes claude"
  fi
done

echo "Restart Claude Code to pick up newly installed skills."
