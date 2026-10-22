#!/usr/bin/env bash
# verify-tests-untouched.sh
# Enforces test immutability during Stage 2 (The Coder) based on `.openhands/project.json` (or `TEST_PATHS`).
set -euo pipefail

# Bepaal de start-branch referentie (bijv. origin/feat/issue-<nr> van Worker 1, met fallback naar origin/main)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [ -n "${1:-}" ]; then
  START_REF="$1"
elif [ -n "${START_BRANCH:-}" ]; then
  START_REF="$START_BRANCH"
elif [ -n "$CURRENT_BRANCH" ] && [ "$CURRENT_BRANCH" != "main" ] && git rev-parse --verify "origin/${CURRENT_BRANCH}" >/dev/null 2>&1; then
  START_REF="origin/${CURRENT_BRANCH}"
else
  START_REF="origin/main"
fi

# Lees test_paths uit TEST_PATHS env var of .openhands/project.json (fallback: __tests__)
RESOLVED_TEST_PATHS=()
if [ -n "${TEST_PATHS:-}" ]; then
  IFS=':' read -r -a RESOLVED_TEST_PATHS <<< "$TEST_PATHS"
elif [ -f ".openhands/project.json" ] && command -v python3 >/dev/null 2>&1; then
  while IFS= read -r line; do
    [ -n "$line" ] && RESOLVED_TEST_PATHS+=("$line")
  done < <(python3 -c '
import json, sys
try:
    data = json.load(open(".openhands/project.json", encoding="utf-8"))
    paths = data.get("test_paths") or ["__tests__/"]
    for p in paths:
        p = str(p).strip()
        if p:
            print(p)
except Exception:
    print("__tests__/")
')
fi

if [ "${#RESOLVED_TEST_PATHS[@]}" -eq 0 ]; then
  RESOLVED_TEST_PATHS=("__tests__/")
fi

# Bouw een grep-expressie voor alle geconfigureerde test_paths
GREP_PARTS=()
for raw_path in "${RESOLVED_TEST_PATHS[@]}"; do
  cleaned="${raw_path%/}"
  cleaned="${cleaned#./}"
  [ -n "$cleaned" ] && GREP_PARTS+=("$cleaned")
done
GREP_PATTERN=$(IFS='|'; echo "${GREP_PARTS[*]}")

# Vergelijk gewijzigde bestanden ten opzichte van de start-branch (inclusief uncommitted/staged wijzigingen)
MODIFIED_TESTS=$(
  {
    git diff --name-only "${START_REF}...HEAD" 2>/dev/null || true
    git diff --name-only HEAD 2>/dev/null || true
    git diff --cached --name-only 2>/dev/null || true
  } | grep -E "(^|/)($GREP_PATTERN)(/|$)" | sort -u || true
)

if [ -n "$MODIFIED_TESTS" ]; then
  echo "❌ CRITICAL GUARDRAIL TRIGGERED:"
  echo "The Coder modified test files in protected test_paths (${RESOLVED_TEST_PATHS[*]}), which is strictly prohibited:"
  echo "$MODIFIED_TESTS"
  echo "Reverting test changes and failing build..."
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    git checkout "$START_REF" -- "$file" 2>/dev/null || \
      git checkout HEAD -- "$file" 2>/dev/null || \
      git checkout origin/main -- "$file" 2>/dev/null || true
  done <<< "$MODIFIED_TESTS"
  exit 1
fi

echo "✅ Tests untouched (${RESOLVED_TEST_PATHS[*]}). Verification valid."
