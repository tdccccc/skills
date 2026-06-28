#!/usr/bin/env bash
set -euo pipefail

DEFAULT_REPO_URL="https://github.com/tdccccc/skills.git"
DEFAULT_REPO_REF="main"
DEFAULT_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"

REPO_URL="${SKILLS_REPO_URL:-$DEFAULT_REPO_URL}"
REPO_REF="${SKILLS_REPO_REF:-$DEFAULT_REPO_REF}"
REPO_DIR="${SKILLS_REPO_DIR:-$DEFAULT_CODEX_HOME/skill-repos/personal-skills}"

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
  curl -fsSL .../bootstrap.sh | bash -s -- --force
  curl -fsSL .../bootstrap.sh | bash -s -- --link
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

need_cmd git

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
bash ./install.sh "$@"
