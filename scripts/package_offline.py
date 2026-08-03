#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "site" / "index.html"
DIST = ROOT / "dist"
VERSION = "v0.3.0-F10.1"
BASE = f"Silk-Road-{VERSION}"
OUT = DIST / f"{BASE}-offline.zip"

DIST.mkdir(exist_ok=True)
html = HTML.read_bytes()
readme = f"""SILK ROAD — {VERSION}\n\nA short browser-based trade visual novel.\n\nHOW TO PLAY\n1. Extract this ZIP.\n2. Open PLAY_SILK_ROAD.html in a modern browser.\n3. Click, tap, or press a key once to permit audio playback.\n\nProgress and audio preferences are stored in that browser's local storage.\nNo internet connection is required after extraction.\n\nCredits for CC0 ambience and effects are available in the in-game Audio menu.\n""".encode("utf-8")

stamp = (2026, 8, 2, 0, 0, 0)
with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for name, payload in [
        (f"{BASE}/PLAY_SILK_ROAD.html", html),
        (f"{BASE}/README.txt", readme),
    ]:
        info = zipfile.ZipInfo(name, date_time=stamp)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        zf.writestr(info, payload)

sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
(OUT.with_suffix(OUT.suffix + ".sha256")).write_text(f"{sha}  {OUT.name}\n", encoding="utf-8")
print(OUT)
print(f"sha256: {sha}")
