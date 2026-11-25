#!/usr/bin/env python3
"""Render every mockup in a design handoff bundle to PNG with headless Chromium.

Usage: render_mockups.py <bundle-dir> [--out DIR] [--chrome PATH] [--prop key=value ...]

Works on temporary copies; mockup sources are never modified.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

DEFAULT_SIZE = (1440, 900)


def find_chrome(explicit):
    for c in [explicit, os.environ.get("CHROME")]:
        if c and os.path.exists(c):
            return c
    pats = ["~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome",
            "~/.cache/ms-playwright/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"]
    for p in pats:
        hits = sorted(glob.glob(os.path.expanduser(p)))
        if hits:
            return hits[-1]
    for name in ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]:
        w = shutil.which(name)
        if w:
            return w
    sys.exit("No Chromium found. Pass --chrome or set $CHROME.")


def read_props(src):
    m = re.search(r"data-props='([^']*)'", src) or re.search(r'data-props="([^"]*)"', src)
    if not m:
        return {}
    try:
        return json.loads(html.unescape(m.group(1)))
    except json.JSONDecodeError:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--out")
    ap.add_argument("--chrome")
    ap.add_argument("--prop", action="append", default=[])
    a = ap.parse_args()

    bundle = os.path.abspath(a.bundle)
    mdir = os.path.join(bundle, "mockups")
    if not os.path.isdir(mdir):
        mdir = bundle
    out = os.path.abspath(a.out or os.path.join(bundle, "screenshots"))
    os.makedirs(out, exist_ok=True)
    chrome = find_chrome(a.chrome)
    overrides = dict(p.split("=", 1) for p in a.prop)

    boards = {}
    cj = os.path.join(mdir, "canvas.json")
    if os.path.exists(cj):
        with open(cj) as f:
            boards = json.load(f).get("boards", {})

    files = sorted(glob.glob(os.path.join(mdir, "*.dc.html")) or glob.glob(os.path.join(mdir, "*.html")))
    if not files:
        sys.exit(f"No mockups found in {mdir}")

    failed = 0
    tmp = tempfile.mkdtemp(prefix="render-mockups-")
    for path in files:
        name = os.path.basename(path)
        stem = re.sub(r"(\.dc)?\.html$", "", name)
        with open(path, encoding="utf-8") as f:
            src = f.read()
        props = read_props(src)
        values = {k: v.get("default") for k, v in props.items() if isinstance(v, dict) and "default" in v}
        values.update(overrides)
        for k, v in values.items():
            if isinstance(v, str):
                src = src.replace("{{" + k + "}}", v)
        if not os.path.exists(os.path.join(mdir, "support.js")):
            src = re.sub(r'<script src="\./support\.js"></script>\s*', "", src)
        b = boards.get(name, {})
        prev = props.get("$preview", {}) if isinstance(props.get("$preview"), dict) else {}
        w = b.get("w") or prev.get("width") or DEFAULT_SIZE[0]
        h = b.get("h") or prev.get("height") or DEFAULT_SIZE[1]
        leftover = len(re.findall(r"\{\{[^}]+\}\}", src))

        # Keep the copy next to the original's siblings so relative links resolve.
        work = os.path.join(tmp, name)
        with open(work, "w", encoding="utf-8") as f:
            f.write(src)
        for sib in os.listdir(mdir):
            sp = os.path.join(mdir, sib)
            dp = os.path.join(tmp, sib)
            if os.path.isfile(sp) and not sib.endswith(".html") and not os.path.exists(dp):
                shutil.copy(sp, dp)

        png = os.path.join(out, stem + ".png")
        cmd = [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
               f"--window-size={w},{h}", "--virtual-time-budget=3000",
               f"--screenshot={png}", "file://" + work]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        except subprocess.TimeoutExpired:
            pass
        ok = os.path.exists(png) and os.path.getsize(png) > 0 and leftover == 0
        failed += 0 if ok else 1
        title = b.get("title", "")
        status = "OK  " if ok else "FAIL"
        print(f"{status} {stem:<22} {w}x{h:<5} props={json.dumps(values)} leftover={{{{={leftover}  {title}")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(files) - failed}/{len(files)} rendered to {out}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
