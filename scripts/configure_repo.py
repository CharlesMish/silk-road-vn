#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser(description="Fill public repository URL placeholders.")
parser.add_argument("owner")
parser.add_argument("repo")
args = parser.parse_args()

pages_url = f"https://{args.owner}.github.io/{args.repo}/"
repo_url = f"https://github.com/{args.owner}/{args.repo}"
release_url = f"{repo_url}/releases/latest"
replacements = {
    "{{PAGES_URL}}": pages_url,
    "{{REPO_URL}}": repo_url,
    "{{RELEASE_URL}}": release_url,
}

for relative in ["README.md"]:
    path = ROOT / relative
    text = path.read_text("utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    if "{{" in text or "}}" in text:
        raise SystemExit(f"unresolved placeholder in {path}")
    path.write_text(text, encoding="utf-8")

print(f"Configured repository: {repo_url}")
print(f"Expected Pages URL: {pages_url}")
