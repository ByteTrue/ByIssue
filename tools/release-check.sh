#!/usr/bin/env bash
# Run every mechanical release check, then confirm the copy the host loads matches skills/bi/.
#
# Usage: bash tools/release-check.sh <deployed-skill-dir> | --no-deploy
#   The deployed copy is the directory the host actually loads (an `npx skills` install puts it in
#   ~/.agents/skills/bi; an index install such as magpie puts it elsewhere). It comes from the
#   argument, else $BI_DEPLOYED; there is no guessed default, because syncing to a copy the host
#   does not load is how the copy fell a version behind twice
#   (byissue/issues/015-x-ff-grilling-verbatim-upstream.md, byissue/issues/016-x-ff-absorb-upstream-grill-family.md).
#   --no-deploy skips only the deployed-copy comparison: use it right after editing, before syncing.
# Exits 1 at the end if any step failed; every step runs so one report shows all failures.
set -uo pipefail
cd "$(dirname "$0")/.."

failed=()
step() {
  echo "== $1"
  if "${@:2}"; then echo; else failed+=("$1"); echo; fi
}

step "checker" python3 tools/check-skill-repository.py
step "checker self-test" python3 tools/check-skill-repository-selftest.py
step "close.md search command" python3 tools/check-close-reference-command.py
step "packaged scripts" python3 tools/check-skill-scripts.py

target="${1:-${BI_DEPLOYED:-}}"
if [ "$target" = "--no-deploy" ]; then
  echo "== deployed copy: skipped (--no-deploy)"
elif [ -z "$target" ]; then
  echo "== deployed copy: not given; pass the directory the host loads (or set BI_DEPLOYED), or --no-deploy before syncing"
  failed+=("deployed copy")
elif [ ! -d "$target" ]; then
  echo "== deployed copy: $target does not exist"
  failed+=("deployed copy")
else
  step "deployed copy matches skills/bi/ ($target)" diff -rq skills/bi "$target"
fi

if [ ${#failed[@]} -gt 0 ]; then
  printf 'release check failed: %s\n' "${failed[*]}"
  exit 1
fi
echo "release check passed"
