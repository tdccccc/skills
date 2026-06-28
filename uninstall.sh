#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
DEFAULT_CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
TARGET="claude"
TARGET_EXPLICIT=0
DEST_OVERRIDE=""
DRY_RUN=0
ASSUME_YES=0

# Top-level names this repo installed in older versions, before skills became
# self-contained. They no longer exist as root-level skills, so they are listed
# explicitly to clean them up from prior installs.
LEGACY_NAMES=(shared tools)

usage() {
  cat <<'USAGE'
Usage: uninstall.sh [options]

Remove this repository's skills from Claude Code and/or Codex.

Only directories this repository installs are removed, looked up by name:
the current root-level skills plus legacy names from older layouts (shared,
tools). Skills from other sources that happen to live in the same directory
are never touched.

Options:
  --target TARGET  Uninstall target: claude, codex, or both
                   Default: ask which target; Enter selects claude
  --dest DIR       Remove from DIR instead of the selected target's skills dir
                   May not be used with --target both
  --yes            Do not prompt for confirmation before removing
  --dry-run        Print what would be removed without deleting anything
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
    --yes|-y)
      ASSUME_YES=1
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
  printf 'Uninstall this repository'\''s skills from which tool?\n' >&3
  printf '  1) Claude Code (default)\n' >&3
  printf '  2) Codex\n' >&3
  printf '  3) Both\n' >&3
  printf 'Choose [1/2/3]: ' >&3
  answer=""
  if IFS= read -r answer <&3; then
    case "$answer" in
      ""|1|claude|Claude) TARGET="claude" ;;
      2|codex|Codex)      TARGET="codex" ;;
      3|both|Both)        TARGET="both" ;;
      *)
        echo "error: invalid choice: $answer" >&2
        exit 2
        ;;
    esac
  fi
  exec 3>&-
fi

if [[ "$TARGET" == "both" && -n "$DEST_OVERRIDE" ]]; then
  echo "error: --dest may not be used with --target both" >&2
  exit 2
fi

# Build the set of owned names: current root-level skills plus legacy names.
owned_names=()
for skill_file in "$ROOT_DIR"/*/SKILL.md; do
  [[ -f "$skill_file" ]] || continue
  owned_names+=("$(basename "$(dirname "$skill_file")")")
done
owned_names+=("${LEGACY_NAMES[@]}")

if [[ "${#owned_names[@]}" -eq 0 ]]; then
  echo "error: no owned skill names resolved under $ROOT_DIR" >&2
  exit 1
fi

# Collect the concrete paths that exist and would be removed, as "target|path".
to_remove=()

collect_target() {
  local target_name="$1"
  local dest_dir="$2"
  local name
  local path

  if [[ ! -d "$dest_dir" ]]; then
    echo "Target $target_name: $dest_dir does not exist, nothing to remove."
    return 0
  fi

  for name in "${owned_names[@]}"; do
    path="$dest_dir/$name"
    # Match real dirs and symlinks; look up strictly by owned name so unrelated
    # skills in the same directory are never considered.
    if [[ -e "$path" || -L "$path" ]]; then
      to_remove+=("$target_name|$path")
    fi
  done
}

case "$TARGET" in
  claude)
    collect_target "claude" "${DEST_OVERRIDE:-$DEFAULT_CLAUDE_CONFIG_DIR/skills}"
    ;;
  codex)
    collect_target "codex" "${DEST_OVERRIDE:-$DEFAULT_CODEX_HOME/skills}"
    ;;
  both)
    collect_target "claude" "$DEFAULT_CLAUDE_CONFIG_DIR/skills"
    collect_target "codex" "$DEFAULT_CODEX_HOME/skills"
    ;;
esac

if [[ "${#to_remove[@]}" -eq 0 ]]; then
  echo "No skills from this repository found to remove."
  exit 0
fi

echo "The following installed skill directories will be removed:"
for entry in "${to_remove[@]}"; do
  echo "  [${entry%%|*}] ${entry#*|}"
done

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run: nothing was deleted."
  exit 0
fi

if [[ "$ASSUME_YES" -ne 1 ]]; then
  if { exec 3<> /dev/tty; } 2>/dev/null; then
    printf 'Remove these %d director(ies)? [y/N] ' "${#to_remove[@]}" >&3
    answer=""
    IFS= read -r answer <&3 || answer=""
    exec 3>&-
    case "$answer" in
      y|Y|yes|YES|Yes) ;;
      *)
        echo "Aborted. Nothing was removed."
        exit 0
        ;;
    esac
  else
    echo "error: refusing to remove without confirmation; pass --yes or use --dry-run" >&2
    exit 1
  fi
fi

for entry in "${to_remove[@]}"; do
  path="${entry#*|}"
  echo "Removing $path"
  rm -rf "$path"
done

echo "Done. Restart Claude Code and/or Codex to drop the removed skills."
