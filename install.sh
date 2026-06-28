#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
DEFAULT_CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
TARGET="claude"
DEST_OVERRIDE=""
LINK_MODE=0
FORCE=0
DRY_RUN=0

usage() {
  cat <<'USAGE'
Usage: install.sh [options]

Install every root-level skill in this repository into Claude Code and/or Codex.
Supporting repository directories used by the skills, such as shared/ and tools/,
are installed alongside the skills.

Options:
  --target TARGET  Install target: claude, codex, or both. Default: claude
  --dest DIR       Install into DIR instead of the selected target's skills dir
                   May not be used with --target both
  --link           Symlink directories instead of copying them
  --force          Replace existing installed directories
  --dry-run        Print actions without changing files
  -h, --help       Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      if [[ $# -lt 2 ]]; then
        echo "error: --target requires claude, codex, or both" >&2
        exit 2
      fi
      TARGET="$2"
      shift 2
      ;;
    --dest)
      if [[ $# -lt 2 ]]; then
        echo "error: --dest requires a directory" >&2
        exit 2
      fi
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

case "$TARGET" in
  claude|codex|both)
    ;;
  *)
    echo "error: --target must be claude, codex, or both" >&2
    exit 2
    ;;
esac

if [[ "$TARGET" == "both" && -n "$DEST_OVERRIDE" ]]; then
  echo "error: --dest may not be used with --target both" >&2
  exit 2
fi

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '+'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

install_dir() {
  local dest_dir="$1"
  local src="$2"
  local target_name="$3"
  local name
  local dest

  name="$(basename "$src")"
  dest="$dest_dir/$name"

  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$FORCE" -eq 1 ]]; then
      echo "Replacing $target_name:$name at $dest"
      run rm -rf "$dest"
    else
      echo "Skipping $target_name:$name: $dest already exists (use --force to replace)"
      return 0
    fi
  fi

  if [[ "$LINK_MODE" -eq 1 ]]; then
    echo "Linking $target_name:$name -> $dest"
    run ln -s "$src" "$dest"
  else
    echo "Installing $target_name:$name -> $dest"
    run cp -R "$src" "$dest"
  fi
}

install_collection() {
  local target_name="$1"
  local dest_dir="$2"
  local src

  echo "Target: $target_name"
  echo "Destination: $dest_dir"
  run mkdir -p "$dest_dir"

  for src in "${skill_dirs[@]}"; do
    install_dir "$dest_dir" "$src" "$target_name"
  done

  for src in "${support_dirs[@]}"; do
    install_dir "$dest_dir" "$src" "$target_name"
  done
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

support_dirs=()
for support_name in shared tools; do
  if [[ -d "$ROOT_DIR/$support_name" ]]; then
    support_dirs+=("$ROOT_DIR/$support_name")
  fi
done

echo "Installing skills from $ROOT_DIR"

case "$TARGET" in
  claude)
    install_collection "claude" "${DEST_OVERRIDE:-$DEFAULT_CLAUDE_CONFIG_DIR/skills}"
    echo "Restart Claude Code to pick up newly installed skills."
    ;;
  codex)
    install_collection "codex" "${DEST_OVERRIDE:-$DEFAULT_CODEX_HOME/skills}"
    echo "Restart Codex to pick up newly installed skills."
    ;;
  both)
    install_collection "claude" "$DEFAULT_CLAUDE_CONFIG_DIR/skills"
    install_collection "codex" "$DEFAULT_CODEX_HOME/skills"
    echo "Restart Claude Code and Codex to pick up newly installed skills."
    ;;
esac
