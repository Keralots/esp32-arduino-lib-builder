#!/bin/bash
# Put rebuilt esp32p4 / esp32p4_es folders into the released libs archive.
# usage: combine.sh STOCK.tar.xz NAME P4_ARTIFACT_DIR P4_ES_ARTIFACT_DIR
set -euo pipefail
stock=$1; name=$2; p4=$3; p4es=$4
out="esp32-core-3.3.8-libs-$name.tar.xz"
work=$(mktemp -d)
mkdir "$work/stock" "$work/p4" "$work/p4es"
tar -xJf "$stock" -C "$work/stock"
# The archive may wrap everything in one top folder.
root="$work/stock"
if [ "$(ls "$root" | wc -l)" = 1 ] && [ -d "$root/$(ls "$root")" ]; then root="$root/$(ls "$root")"; fi
test -f "$root/package.json"
tar -xzf "$p4"/arduino-esp32-libs-esp32p4-*.tar.gz -C "$work/p4"
tar -xzf "$p4es"/arduino-esp32-libs-esp32p4_es-*.tar.gz -C "$work/p4es"
for pair in "esp32p4:$work/p4" "esp32p4_es:$work/p4es"; do
  t=${pair%%:*}; src="${pair#*:}/tools/esp32-arduino-libs/$t"
  test -d "$src"
  echo "::group::$name sdkconfig $t: released vs rebuilt"
  diff "$root/$t/sdkconfig" "$src/sdkconfig" || true
  echo "::endgroup::"
  rm -rf "${root:?}/$t"
  cp -a "$src" "$root/$t"
done
python3 - "$root/package.json" "$name" <<'PY'
import json, sys
p, name = sys.argv[1], sys.argv[2]
d = json.load(open(p))
d["version"] += "." + name.replace("-", ".")
json.dump(d, open(p, "w"), indent=2)
print(d["version"])
PY
printf '\np4 rebuilt (%s): %s %s\n' "$name" "${GITHUB_REPOSITORY:-local}" "${GITHUB_SHA:-}" >> "$root/versions.txt"
tar -cJf "$out" -C "$root" .
sha256sum "$out" | tee "$out.sha256"
ls -la "$out"
rm -rf "$work"
