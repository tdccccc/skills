#!/usr/bin/env bash
set -euo pipefail

DEFAULT_REPO_URL="https://github.com/tdccccc/skills.git"
DEFAULT_REPO_REF="main"
DEFAULT_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

REPO_URL="${SKILLS_REPO_URL:-$DEFAULT_REPO_URL}"
REPO_REF="${SKILLS_REPO_REF:-$DEFAULT_REPO_REF}"
REPO_DIR="${SKILLS_REPO_DIR:-$DEFAULT_CACHE_HOME/tdccccc-skills}"

TARGET_CHOSEN=""

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "error: required command not found: $1" >&2
    exit 127
  fi
}

usage() {
  cat <<'USAGE'
Usage:
  curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash

Bootstrap options are configured with environment variables:
  SKILLS_REPO_URL   Git repository URL to clone
  SKILLS_REPO_REF   Git branch or tag to install, default: main
  SKILLS_REPO_DIR   Local repository cache directory

Arguments passed to this script are forwarded to install.sh:
  curl -fsSL .../bootstrap.sh | bash
      Ask which tool(s) to install before downloading; Cancel aborts without
      cloning anything.
  curl -fsSL .../bootstrap.sh | bash -s -- --target claude
  curl -fsSL .../bootstrap.sh | bash -s -- --target codex
  curl -fsSL .../bootstrap.sh | bash -s -- --target both
  curl -fsSL .../bootstrap.sh | bash -s -- --force
  curl -fsSL .../bootstrap.sh | bash -s -- --link
USAGE
}

has_target_arg() {
  local arg
  for arg in "$@"; do
    case "$arg" in
      --target|--target=*)
        return 0
        ;;
    esac
  done
  return 1
}

prompt_target() {
  # Skip when the caller already passed --target explicitly.
  if has_target_arg "$@"; then
    return 0
  fi

  # Skip when there is no terminal to prompt on; install.sh applies its default.
  if ! { exec 3<>/dev/tty; } 2>/dev/null; then
    return 0
  fi

  printf '\n' >&3
  printf 'Install skills for which tool?\n' >&3
  printf '  1) Claude Code (default)\n' >&3
  printf '  2) Codex\n' >&3
  printf '  3) Both\n' >&3
  printf '  q) Cancel\n' >&3
  printf 'Choose [1/2/3/q]: ' >&3

  local answer=""
  IFS= read -r answer <&3 || answer=""
  exec 3>&-

  case "$answer" in
    ""|1|claude|Claude)
      TARGET_CHOSEN="claude"
      ;;
    2|codex|Codex)
      TARGET_CHOSEN="codex"
      ;;
    3|both|Both)
      TARGET_CHOSEN="both"
      ;;
    q|Q|quit|cancel|Cancel)
      echo "Aborted. Nothing was cloned or installed."
      exit 0
      ;;
    *)
      echo "error: invalid choice: $answer" >&2
      exit 2
      ;;
  esac
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

need_cmd git

# Ask the install target before any download so Cancel costs nothing. The
# choice is forwarded as --target, which suppresses install.sh's own prompt.
# install.sh replaces existing skills by default, so bootstrap always updates.
forward_args=("$@")
prompt_target "$@"
if [[ -n "$TARGET_CHOSEN" ]]; then
  forward_args=(--target "$TARGET_CHOSEN" "$@")
fi

echo "Repository: $REPO_URL"
echo "Reference: $REPO_REF"
echo "Local cache: $REPO_DIR"

if [[ -d "$REPO_DIR/.git" ]]; then
  current_origin="$(git -C "$REPO_DIR" config --get remote.origin.url || true)"
  if [[ "$current_origin" != "$REPO_URL" ]]; then
    echo "error: $REPO_DIR already exists with a different origin:" >&2
    echo "  current: ${current_origin:-<none>}" >&2
    echo "  expected: $REPO_URL" >&2
    echo "Set SKILLS_REPO_DIR to another path or move the existing directory." >&2
    exit 1
  fi

  echo "Updating cached repository"
  git -C "$REPO_DIR" fetch --depth 1 origin "$REPO_REF"
  git -C "$REPO_DIR" checkout -q --detach FETCH_HEAD
else
  if [[ -e "$REPO_DIR" ]]; then
    echo "error: $REPO_DIR exists but is not a git repository" >&2
    echo "Set SKILLS_REPO_DIR to another path or move the existing directory." >&2
    exit 1
  fi

  mkdir -p "$(dirname "$REPO_DIR")"
  echo "Cloning repository"
  git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$REPO_DIR"
fi

if [[ ! -f "$REPO_DIR/install.sh" ]]; then
  echo "error: install.sh not found in $REPO_DIR" >&2
  exit 1
fi

cd "$REPO_DIR"
bash ./install.sh ${forward_args[@]+"${forward_args[@]}"}
