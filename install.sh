#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
DEST_DIR="$DEFAULT_CODEX_HOME/skills"
LINK_MODE=0
FORCE=0
DRY_RUN=0

usage() {
  cat <<'USAGE'
Usage: install.sh [options]

Install every root-level skill in this repository into Codex's skills directory.
Supporting repository directories used by the skills, such as shared/ and tools/,
are installed alongside the skills.

Options:
  --dest DIR   Install into DIR instead of ${CODEX_HOME:-$HOME/.codex}/skills
  --link       Symlink directories instead of copying them
  --force      Replace existing installed directories
  --dry-run    Print actions without changing files
  -h, --help   Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      if [[ $# -lt 2 ]]; then
        echo "error: --dest requires a directory" >&2
        exit 2
      fi
      DEST_DIR="$2"
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
  local src="$1"
  local name
  local dest

  name="$(basename "$src")"
  dest="$DEST_DIR/$name"

  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$FORCE" -eq 1 ]]; then
      echo "Replacing $name at $dest"
      run rm -rf "$dest"
    else
      echo "Skipping $name: $dest already exists (use --force to replace)"
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

support_dirs=()
for support_name in shared tools; do
  if [[ -d "$ROOT_DIR/$support_name" ]]; then
    support_dirs+=("$ROOT_DIR/$support_name")
  fi
done

echo "Installing skills from $ROOT_DIR"
echo "Destination: $DEST_DIR"
run mkdir -p "$DEST_DIR"

for dir in "${skill_dirs[@]}"; do
  install_dir "$dir"
done

for dir in "${support_dirs[@]}"; do
  install_dir "$dir"
done

echo "Restart Codex to pick up newly installed skills."
