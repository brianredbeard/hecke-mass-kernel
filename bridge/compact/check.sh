#!/usr/bin/env bash
set -euo pipefail

fail() { echo "$*" >&2; exit 1; }
[[ $# == 1 ]] || fail "Usage: bash bridge/compact/check.sh /path/to/grh-compact"
here=$(cd "$(dirname "$0")" && pwd)
kernel=$(cd "$here/../../lean" && pwd)
cd "$1" || fail "Cannot open compact checkout: $1"

compact_rev=72fead102f663d5c7a407964a13dc0cf9d977207
mathlib_rev=56a005855ea17e0b0958f73ec801ae140b0a1679
[[ $(git rev-parse HEAD) == "$compact_rev" ]] || fail "Expected compact revision $compact_rev"
[[ -f lake-manifest.json ]] || fail "Missing compact lake-manifest.json"
locked_mathlib=$(python3 -c '
import json
with open("lake-manifest.json") as manifest:
    print(next((p["rev"] for p in json.load(manifest)["packages"] if p["name"] == "mathlib"), "missing"))
')
[[ $locked_mathlib == "$mathlib_rev" ]] || fail "Expected Mathlib manifest revision $mathlib_rev"
[[ $(git -C .lake/packages/mathlib rev-parse HEAD) == "$mathlib_rev" ]] || fail "Expected Mathlib checkout $mathlib_rev"

for module in Main Lib/Adelic/Hecke/HeckeBasic Lib/Adelic/Hecke/ClassMean; do
  [[ -s .lake/build/lib/lean/$module.olean ]] || fail "Missing compiled compact module: $module.olean"
done
if [[ -x .lake/research-toolchain/bin/lake ]]; then
  export PATH="$PWD/.lake/research-toolchain/bin:$PATH"
fi
unset LEAN_PATH
version=$(lake env lean --version)
[[ $version == 'Lean (version 4.35.0,'* ]] || fail "Expected Lean 4.35.0, found $version"

work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
mkdir "$work/HeckeMassKernel"
compile() {
  local root=$1 module=$2
  lake env bash -c 'export LEAN_PATH="$1:$LEAN_PATH"; shift; exec lean "$@"' \
    _ "$work" --root="$root" -o "$work/$module.olean" "$root/$module.lean"
}
compile "$kernel" HeckeMassKernel/Finite
for module in Minimal ProjectBridge KernelBridge; do
  compile "$here" "$module" | tee -a "$work/axioms.log"
done

python3 - "$work/axioms.log" <<'PY'
from pathlib import Path
import re
import sys

log = Path(sys.argv[1]).read_text()
allowed = {"propext", "Classical.choice", "Quot.sound"}
for name in ("KernelCompact.mass_eq", "KernelCompact.mass_classSum_real",
             "KernelCompact.hecke_value", "ResearchMass.weightedSum_heckeFun"):
    report = re.search(rf"^'{re.escape(name)}' (?:does not depend on any axioms|"
                       r"depends on axioms:\s*\[([^\]]*)\])$", log, re.MULTILINE)
    if report is None:
        sys.exit(f"Missing axiom report for {name}")
    extra = {a.strip() for a in (report[1] or "").split(",") if a.strip()} - allowed
    if extra:
        sys.exit(f"Unexpected axioms for {name}: {', '.join(sorted(extra))}")
PY
