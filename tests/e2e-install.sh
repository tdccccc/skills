#!/usr/bin/env bash
# End-to-end install/uninstall test in an ISOLATED sandbox.
#
# Downloads this repo from GitHub via bootstrap.sh, installs into throwaway
# directories, verifies the per-target layout, then uninstalls and verifies
# removal. Your real ~/.claude and ~/.codex are never touched, because the
# sandbox overrides SKILLS_REPO_DIR, CLAUDE_CONFIG_DIR, and CODEX_HOME.
#
# Usage:
#   bash tests/e2e-install.sh [git-ref]      # default ref: main
#   KEEP_SANDBOX=1 bash tests/e2e-install.sh # keep the sandbox for inspection
set -uo pipefail

REF="${1:-main}"
REPO_SLUG="tdccccc/skills"
RAW_URL="https://raw.githubusercontent.com/$REPO_SLUG/$REF/bootstrap.sh"

SANDBOX="$(mktemp -d "${TMPDIR:-/tmp}/skills-e2e.XXXXXX")" || {
  echo "error: could not create sandbox" >&2; exit 1; }

export SKILLS_REPO_DIR="$SANDBOX/cache"
export SKILLS_REPO_REF="$REF"
export CLAUDE_CONFIG_DIR="$SANDBOX/claude"
export CODEX_HOME="$SANDBOX/codex"

CS="$CLAUDE_CONFIG_DIR/skills"
XS="$CODEX_HOME/skills"

if [ -t 1 ]; then G=$'\033[32m'; R=$'\033[31m'; B=$'\033[1m'; Z=$'\033[0m'
else G=; R=; B=; Z=; fi

pass=0; fail=0
ok(){ printf '  %sPASS%s %s\n' "$G" "$Z" "$1"; pass=$((pass+1)); }
bad(){ printf '  %sFAIL%s %s\n' "$R" "$Z" "$1"; fail=$((fail+1)); }
have(){   if [ -e "$1" ] || [ -L "$1" ]; then ok "$2"; else bad "$2 -- missing: $1"; fi; }
absent(){ if [ -e "$1" ] || [ -L "$1" ]; then bad "$2 -- unexpected: $1"; else ok "$2"; fi; }

cleanup(){
  if [ "${KEEP_SANDBOX:-0}" = 1 ]; then
    echo; echo "Sandbox kept at: $SANDBOX"
  else
    rm -rf "$SANDBOX"
  fi
}
trap cleanup EXIT

printf '%sSandbox:%s %s\n' "$B" "$Z" "$SANDBOX"
printf '%sRef:%s     %s\n' "$B" "$Z" "$REF"
printf '%sSource:%s  %s\n' "$B" "$Z" "$RAW_URL"
echo

echo "${B}== Install (--target both) ==${Z}"
if ! curl -fsSL "$RAW_URL" | bash -s -- --target both; then
  echo "${R}bootstrap/install failed${Z}" >&2
  exit 1
fi
echo

echo "${B}== Verify Claude side ==${Z}"
have   "$CS/article-summary"     "article-summary installed"
have   "$CS/claude-codex-runner" "claude-codex-runner installed"
have   "$CS/grill-me"            "grill-me installed"
have   "$CS/security-audit"      "security-audit installed"
absent "$CS/codex-task-executor" "codex-task-executor excluded from claude"
absent "$CS/shared"              "no stray shared/ at claude top level"
absent "$CS/tools"               "no stray tools/ at claude top level"
have   "$CS/claude-codex-runner/tools/codex-runner/codex-runner"   "runner nested inside its skill"
have   "$CS/claude-codex-runner/references/codex-task-contract.md" "contract nested inside its skill"
runner="$CS/claude-codex-runner/tools/codex-runner/codex-runner"
if [ -x "$runner" ] && "$runner" --help >/dev/null 2>&1; then
  ok "installed runner executes (--help)"
else
  bad "installed runner does not execute"
fi
echo

echo "${B}== Verify Codex side ==${Z}"
have   "$XS/codex-task-executor" "codex-task-executor installed"
absent "$XS/article-summary"     "article-summary excluded from codex"
absent "$XS/claude-codex-runner" "claude-codex-runner excluded from codex"
absent "$XS/grill-me"            "grill-me excluded from codex"
absent "$XS/security-audit"      "security-audit excluded from codex"
absent "$XS/shared"              "no stray shared/ at codex top level"
absent "$XS/tools"               "no stray tools/ at codex top level"
echo

echo "${B}== Uninstall (--target both --yes) ==${Z}"
if [ ! -f "$SKILLS_REPO_DIR/uninstall.sh" ]; then
  bad "uninstall.sh not found in cloned repo"
else
  bash "$SKILLS_REPO_DIR/uninstall.sh" --target both --yes
fi
echo

echo "${B}== Verify removal ==${Z}"
absent "$CS/article-summary"     "claude article-summary removed"
absent "$CS/claude-codex-runner" "claude claude-codex-runner removed"
absent "$CS/grill-me"            "claude grill-me removed"
absent "$CS/security-audit"      "claude security-audit removed"
absent "$XS/codex-task-executor" "codex codex-task-executor removed"
echo

echo "${B}== Summary ==${Z}"
printf '  %s%d passed%s, %s%d failed%s\n' "$G" "$pass" "$Z" \
  "$( [ "$fail" -gt 0 ] && printf '%s' "$R" || printf '%s' "$G")" "$fail" "$Z"
[ "$fail" -eq 0 ] || exit 1
