#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
DEFAULT_CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
TARGET="claude"
TARGET_EXPLICIT=0
DEST_OVERRIDE=""
LINK_MODE=0
FORCE=1
DRY_RUN=0

usage() {
  cat <<'USAGE'
Usage: install.sh [options]

Install root-level skills from this repository into Claude Code and/or Codex.
Each skill may declare an `install-targets:` field in its SKILL.md frontmatter
(claude, codex, or both); skills that exclude the chosen target are skipped.
A skill without the field defaults to both. Each skill is self-contained: any
helper scripts or reference docs it needs live inside its own directory and are
copied along with it.

Options:
  --target TARGET  Install target: claude, codex, or both
                   Default: ask whether to install both; No installs claude
                   This selects which tools to install into; each skill's
                   install-targets then decides whether it lands there.
  --dest DIR       Install into DIR instead of the selected target's skills dir
                   May not be used with --target both
  --link           Symlink directories instead of copying them
  --no-force       Skip skills that already exist instead of replacing them
  --force          Replace existing installed directories (default)
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
      TARGET_EXPLICIT=1
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

case "$TARGET" in
  claude|codex|both)
    ;;
  *)
    echo "error: --target must be claude, codex, or both" >&2
    exit 2
    ;;
esac

if [[ "$TARGET_EXPLICIT" -eq 0 && -z "$DEST_OVERRIDE" ]] && { exec 3<> /dev/tty; } 2>/dev/null; then
  printf 'This installer can install skills for both Claude Code and Codex.\n' >&3
  printf 'Install to both Claude Code and Codex? [y/N] ' >&3
  answer=""
  if IFS= read -r answer <&3; then
    case "$answer" in
      y|Y|yes|YES|Yes)
        TARGET="both"
        ;;
      *)
        TARGET="claude"
        ;;
    esac
  fi
  exec 3>&-
fi

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

# Read the `install-targets` field from a skill's SKILL.md frontmatter.
# Accepts a comma/space separated list of: claude, codex, both.
# Missing field defaults to "both" so existing skills keep installing everywhere.
skill_targets() {
  local skill_dir="$1"
  local skill_file="$skill_dir/SKILL.md"
  local line=""

  if [[ -f "$skill_file" ]]; then
    # Only scan the frontmatter block (between the first two `---` lines).
    line="$(awk '
      NR==1 && $0=="---" { in_fm=1; next }
      in_fm && $0=="---" { exit }
      in_fm && tolower($0) ~ /^install-targets[[:space:]]*:/ {
        sub(/^[^:]*:[[:space:]]*/, "")
        print
        exit
      }
    ' "$skill_file")"
  fi

  if [[ -z "$line" ]]; then
    echo "both"
    return 0
  fi

  # Normalize separators and lowercase.
  echo "$line" | tr ',' ' ' | tr '[:upper:]' '[:lower:]'
}

# Return success if the skill should be installed for the given target.
skill_wants_target() {
  local skill_dir="$1"
  local target_name="$2"
  local token

  for token in $(skill_targets "$skill_dir"); do
    case "$token" in
      both)
        return 0
        ;;
      "$target_name")
        return 0
        ;;
    esac
  done
  return 1
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
      echo "Skipping $target_name:$name: $dest already exists (omit --no-force to replace)"
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
    if skill_wants_target "$src" "$target_name"; then
      install_dir "$dest_dir" "$src" "$target_name"
    else
      echo "Skipping $target_name:$(basename "$src"): install-targets excludes $target_name"
    fi
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
