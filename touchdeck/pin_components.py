#!/usr/bin/env python3
"""Pin component versions to a released dependencies.lock, or check a build against it.

usage: pin_components.py pin LOCK MAIN_MANIFEST [OTHER_MANIFEST ...]
       pin_components.py check BUILT_LOCK LOCK
Registry components only; git, local and idf entries are left alone.
"""
import re
import sys


def read_lock(path):
    """{name: version} of registry components in an IDF dependencies.lock."""
    pins, name, version, kind = {}, None, None, None
    in_deps = False

    def flush():
        if name and kind == "service" and version:
            pins[name] = version

    for line in open(path, encoding="utf-8").read().splitlines():
        if not line.startswith(" "):
            flush()
            name = None
            in_deps = line.startswith("dependencies:")
            continue
        if not in_deps:
            continue
        m = re.match(r"^  (\S+):\s*$", line)
        if m:
            flush()
            name, version, kind = m.group(1), None, None
            continue
        m = re.match(r"^    version: '?([^'\s]+)'?\s*$", line)
        if m:
            version = m.group(1)
            continue
        m = re.match(r"^      type: (\w+)\s*$", line)
        if m:
            kind = m.group(1)
    flush()
    return pins


def pin_text(text, name, version):
    """Set the version of dependency `name` in a manifest; None if it is not listed."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"^  " + re.escape(name) + r":(.*)$", line)
        if not m:
            continue
        if m.group(1).strip():
            lines[i] = f'  {name}: "=={version}"'
            return "\n".join(lines)
        for j in range(i + 1, len(lines)):
            if re.match(r"^  \S", lines[j]) or re.match(r"^\S", lines[j]):
                break
            if re.match(r"^    version:", lines[j]):
                lines[j] = f'    version: "=={version}"'
                return "\n".join(lines)
        lines.insert(i + 1, f'    version: "=={version}"')
        return "\n".join(lines)
    return None


def pin(lock, main, others):
    pins = read_lock(lock)
    texts = {p: open(p, encoding="utf-8").read() for p in [main] + others}
    for name, version in sorted(pins.items()):
        done = False
        for p, t in texts.items():
            new = pin_text(t, name, version)
            if new is not None:
                texts[p] = new
                done = True
                print(f"pinned {name} == {version} in {p}")
        if not done:
            # Transitive in the release: listed directly so the solver cannot pick a newer one.
            texts[main] = texts[main].rstrip("\n") + f'\n  {name}:\n    version: "=={version}"\n'
            print(f"added  {name} == {version} to {main}")
    for p, t in texts.items():
        open(p, "w", encoding="utf-8", newline="\n").write(t)


def check(built, lock):
    want, got = read_lock(lock), read_lock(built)
    bad = 0
    for name in sorted(set(want) | set(got)):
        if want.get(name) != got.get(name):
            print(f"MISMATCH {name}: release {want.get(name)} build {got.get(name)}")
            bad += 1
    print(f"{len(got)} components checked, {bad} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "pin":
        pin(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif len(sys.argv) == 4 and sys.argv[1] == "check":
        sys.exit(check(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(__doc__)
