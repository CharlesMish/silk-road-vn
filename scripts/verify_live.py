#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "site" / "index.html"

parser = argparse.ArgumentParser(description="Verify the deployed GitHub Pages copy.")
parser.add_argument("url")
args = parser.parse_args()
url = args.url if args.url.endswith("/") else args.url + "/"

req = urllib.request.Request(url, headers={"User-Agent": "silk-road-release-verifier/1.0"})
with urllib.request.urlopen(req, timeout=60) as response:
    if response.status != 200:
        raise SystemExit(f"unexpected HTTP status: {response.status}")
    remote = response.read()

text = remote.decode("utf-8")
for marker in [
    "<title>Silk Road — Mistress Lan’s Final Road</title>",
    "Mistress Lan’s final road",
    "v0.3.0-F10.1",
    "data:audio/mpeg;base64,",
]:
    if marker not in text:
        raise SystemExit(f"live page missing marker: {marker}")

local = LOCAL.read_bytes()
remote_sha = hashlib.sha256(remote).hexdigest()
local_sha = hashlib.sha256(local).hexdigest()
if remote_sha != local_sha:
    raise SystemExit(f"live bytes differ from local site: {remote_sha} != {local_sha}")

print("PASS: live GitHub Pages copy matches local release")
print(f"url: {url}")
print(f"bytes: {len(remote)}")
print(f"sha256: {remote_sha}")
