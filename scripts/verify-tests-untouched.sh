#!/usr/bin/env bash
# verify-tests-untouched.sh
# Enforces test and contract/guard immutability during Stage 2 (The Coder) based on `.openhands/project.json` (or `TEST_PATHS`).
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

export START_REF

# Gebruik Python om veilig test_paths uit zowel START_REF als de werkboom te laden
# (zodat Stage 2 `.openhands/project.json` niet kan manipuleren om de guard te omzeilen)
# en controleer gewijzigde paden zonder kwetsbare shell-regex interpolatie.
MODIFIED_TESTS=$(python3 - <<'PY'
import json
import os
import subprocess
import sys

start_ref = os.environ.get("START_REF", "origin/main")
env_test_paths = os.environ.get("TEST_PATHS", "").strip()

immutable_guard_files = [
    ".openhands/project.json",
    "verify-tests-untouched.sh",
    "scripts/verify-tests-untouched.sh",
    ".github/workflows",
]

resolved = []
if env_test_paths:
    for part in env_test_paths.split(":"):
        if part.strip():
            resolved.append(part.strip())

# 1. Load trusted test_paths from START_REF:.openhands/project.json
try:
    proc = subprocess.run(
        ["git", "show", f"{start_ref}:.openhands/project.json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        data = json.loads(proc.stdout)
        for p in data.get("test_paths") or []:
            if str(p).strip():
                resolved.append(str(p).strip())
except Exception:
    pass

# 2. Also load test_paths from working tree .openhands/project.json
try:
    if os.path.isfile(".openhands/project.json"):
        with open(".openhands/project.json", encoding="utf-8") as fh:
            data = json.load(fh)
        for p in data.get("test_paths") or []:
            if str(p).strip():
                resolved.append(str(p).strip())
except Exception:
    pass

if not resolved:
    resolved.append("__tests__/")

protected_paths = list(dict.fromkeys([*resolved, *immutable_guard_files]))

def matches_protected(file_path: str, paths: list[str]) -> bool:
    norm_file = file_path.strip().lstrip("./")
    if not norm_file:
        return False
    for raw_tp in paths:
        cleaned = raw_tp.strip().strip("/").lstrip("./")
        if not cleaned:
            continue
        if (
            norm_file == cleaned
            or norm_file.startswith(f"{cleaned}/")
            or f"/{cleaned}/" in norm_file
            or norm_file.endswith(f"/{cleaned}")
        ):
            return True
    return False

diff_cmds = [
    ["git", "diff", "--name-only", f"{start_ref}...HEAD"],
    ["git", "diff", "--name-only", "HEAD"],
    ["git", "diff", "--cached", "--name-only"],
]
changed = set()
for cmd in diff_cmds:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode == 0:
        for line in proc.stdout.splitlines():
            if line.strip():
                changed.add(line.strip())

violating = sorted(f for f in changed if matches_protected(f, protected_paths))
for f in violating:
    print(f)
PY
)

if [ -n "$MODIFIED_TESTS" ]; then
  echo "❌ CRITICAL GUARDRAIL TRIGGERED:"
  echo "The Coder modified protected test or guardrail files, which is strictly prohibited:"
  echo "$MODIFIED_TESTS"
  echo "Reverting protected file changes and failing build..."
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    git checkout "$START_REF" -- "$file" 2>/dev/null || \
      git checkout HEAD -- "$file" 2>/dev/null || \
      git checkout origin/main -- "$file" 2>/dev/null || true
  done <<< "$MODIFIED_TESTS"
  exit 1
fi

echo "✅ Tests and guardrails untouched. Verification valid."
