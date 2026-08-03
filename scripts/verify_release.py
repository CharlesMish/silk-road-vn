#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "site" / "index.html"
HASH_FILE = ROOT / "site" / "index.html.sha256"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


if not HTML.is_file():
    fail(f"missing {HTML}")

data = HTML.read_bytes()
text = data.decode("utf-8")
sha = hashlib.sha256(data).hexdigest()
size = len(data)

if not (1_000_000 < size < 100 * 1024 * 1024):
    fail(f"unexpected HTML size: {size} bytes")

required = [
    "<!doctype html>",
    '<html lang="en"',
    "<title>Silk Road — Mistress Lan’s Final Road</title>",
    "Mistress Lan’s final road",
    "A short Ink-driven trade journey · four cities · one sitting",
    "v0.3.0-F10.1",
    "silkroad:save:v3",
    "silkroad:audio-preferences:v2",
    "data:image/",
    "data:audio/mpeg;base64,",
    "Source credits",
]
for marker in required:
    if marker not in text:
        fail(f"required marker missing: {marker}")

disallowed = [
    "Silk Road — Presentation Candidate F10.1",
    "presentation-ready ledger polish",
    "file://",
    "localhost",
    "127.0.0.1",
    "{{PAGES_URL}}",
    "{{REPO_URL}}",
]
for marker in disallowed:
    if marker in text:
        fail(f"publication marker or local dependency remains in site HTML: {marker}")

external_assets = re.findall(
    r'''(?:src|href)\s*=\s*["']https?://[^"']+["']''', text, flags=re.I
)
if external_assets:
    fail(f"external runtime asset references found: {external_assets[:5]}")

if HASH_FILE.is_file():
    expected = HASH_FILE.read_text("utf-8").split()[0]
    if expected != sha:
        fail(f"site hash changed: expected {expected}, got {sha}")

scripts = re.findall(r"<script\b([^>]*)>(.*?)</script>", text, flags=re.I | re.S)
js_blocks = []
for attrs, body in scripts:
    type_match = re.search(r'''type\s*=\s*["']([^"']+)["']''', attrs, flags=re.I)
    script_type = type_match.group(1).lower() if type_match else "text/javascript"
    if script_type in {"application/json", "application/ld+json"}:
        continue
    js_blocks.append(body)

node = shutil.which("node")
if node:
    with tempfile.TemporaryDirectory() as tmp:
        for i, body in enumerate(js_blocks, start=1):
            path = Path(tmp) / f"inline-{i}.js"
            path.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [node, "--check", str(path)], capture_output=True, text=True
            )
            if result.returncode:
                fail(f"inline JavaScript block {i} failed syntax check:\n{result.stderr}")
else:
    print("WARN: node not found; skipped JavaScript syntax checks")

print("PASS: release payload verified")
print(f"bytes: {size}")
print(f"sha256: {sha}")
print(f"inline JavaScript blocks checked: {len(js_blocks) if node else 0}")
print(f"embedded image markers: {text.count('data:image/')}")
print(f"embedded MPEG markers: {text.count('data:audio/mpeg;base64,')}")
