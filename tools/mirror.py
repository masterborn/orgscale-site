#!/usr/bin/env python3
"""
Mirror orgscale.ai into ./public as a fully self-contained static site.

Walks the dependency graph starting from the HTML entry point: every
framerusercontent.com / fonts.gstatic.com asset it finds is downloaded,
given a stable local path, and every reference to it is rewritten.
Text assets (.html/.mjs/.css/.json) are re-scanned, so lazily imported
font chunks are picked up too.

Usage:  python3 tools/mirror.py
"""

from __future__ import annotations

import os
import re
import sys
import json
import urllib.request
import urllib.error
from collections import deque
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public")

SITE = "https://orgscale.ai/"
FRAMER_SITE_ID = "5LPvpJ6npRwb1XSOkjKcYH"

# Hosts whose assets we pull down and serve ourselves.
LOCALIZE_HOSTS = {"framerusercontent.com", "fonts.gstatic.com"}

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
)

TEXT_EXT = {".html", ".mjs", ".js", ".css", ".json", ".map", ".svg"}

# Matches absolute URLs to the hosts we localize, in HTML attrs, CSS url(),
# JS string literals and srcset lists. Kept deliberately greedy on the
# query string so ?scale-down-to=512 variants are captured as distinct URLs.
URL_RE = re.compile(
    r"https://(?:framerusercontent\.com|fonts\.gstatic\.com)"
    r"[A-Za-z0-9._~:/?#\[\]@!$&'*+,;=%-]+"
)

# Relative ESM specifiers inside Framer chunks: ./chunk-X.mjs, ./google-Y.mjs
REL_MJS_RE = re.compile(r'(?:from|import)\(?"(\./[A-Za-z0-9._-]+\.mjs)"')


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": SITE})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def local_path(url: str) -> str:
    """Map a remote asset URL to a stable path under public/."""
    parts = urlsplit(url)
    host, path, query = parts.netloc, parts.path, parts.query

    # Encode query-string image variants into the filename so
    # foo.png and foo.png?scale-down-to=512 stay distinct files.
    suffix = ""
    if query:
        suffix = "." + re.sub(r"[^A-Za-z0-9]+", "-", query).strip("-")

    def with_suffix(p: str) -> str:
        if not suffix:
            return p
        base, ext = os.path.splitext(p)
        return f"{base}{suffix}{ext}"

    if host == "fonts.gstatic.com":
        # /s/lora/v36/<hash>.woff2 -> assets/fonts/google/lora-<hash>.woff2
        seg = path.strip("/").split("/")
        family = seg[1] if len(seg) > 1 else "font"
        return with_suffix(f"assets/fonts/google/{family}-{seg[-1]}")

    if path.startswith(f"/sites/{FRAMER_SITE_ID}/"):
        return with_suffix("assets/framer/" + path.split("/", 3)[3])

    if path.startswith("/images/"):
        return with_suffix("assets/images/" + path[len("/images/"):])

    if path.startswith("/assets/"):
        # /assets/ on the Framer CDN mixes webfonts with images
        # (favicons, OG image), so route by extension, not by prefix.
        name = path[len("/assets/"):]
        bucket = "fonts/framer" if os.path.splitext(name)[1].lower() in {
            ".woff2", ".woff", ".ttf", ".otf", ".eot",
        } else "images"
        return with_suffix(f"assets/{bucket}/{name}")

    if path.startswith("/third-party-assets/"):
        # .../fontshare/wf/<A>/<B>/<C>.woff2 -> assets/fonts/fontshare/<C>.woff2
        return with_suffix("assets/fonts/fontshare/" + path.rsplit("/", 1)[-1])

    if path.startswith("/modules/"):
        return with_suffix("assets/framer/modules/" + path.rsplit("/", 1)[-1])

    return with_suffix("assets/misc/" + path.rsplit("/", 1)[-1])


def is_text(rel: str) -> bool:
    return os.path.splitext(rel)[1].lower() in TEXT_EXT


# --- Self-hosting patches -------------------------------------------------
# Two references only make sense while Framer hosts the site. Neither has any
# visual effect, but left alone they call out to Framer from our own origin
# and log console errors. Patched here (not by hand) so re-mirroring keeps them.

EDITOR_BAR_STUB = """\
// Local stand-in for https://edit.framer.com/init.mjs
//
// Framer's floating "Editor Bar" only ever renders for a signed-in editor of
// the original Framer project, so on a self-hosted copy it can never show
// anything -- it just triggers a cross-origin request that fails. This stub
// satisfies the dynamic import with a component that renders nothing.
export function createEditorBar() {
  return function EditorBar() {
    return null;
  };
}
export default createEditorBar;
"""

STUB_REL = "assets/framer/editor-bar-stub.mjs"


def patch_file(rel: str, old: str, new: str, label: str) -> None:
    p = os.path.join(OUT, rel)
    if not os.path.exists(p):
        print(f"  ! patch skipped, missing {rel}: {label}")
        return
    with open(p, encoding="utf-8") as f:
        text = f.read()
    if old not in text:
        print(f"  ! patch no-op ({label}) -- pattern not found in {rel}")
        return
    with open(p, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))
    print(f"  patched {rel}: {label}")


def apply_selfhost_patches() -> None:
    print("\n→ applying self-hosting patches")

    with open(os.path.join(OUT, STUB_REL), "w", encoding="utf-8") as f:
        f.write(EDITOR_BAR_STUB)

    # A relative specifier in a dynamic import() resolves against the importing
    # module, not the document -- so this must be a bare sibling reference.
    patch_file(
        "assets/framer/script_main.XZVAIZWD.mjs",
        '"https://edit.framer.com/init.mjs"',
        '"./editor-bar-stub.mjs"',
        "Framer editor bar -> local stub",
    )

    # Framer's own page-view beacon, keyed to the Framer-hosted deployment.
    patch_file(
        "index.html",
        '<script async src="https://events.framer.com/script?v=2"',
        "<!-- Framer analytics beacon, disabled on the self-hosted copy\n"
        '    <script async src="https://events.framer.com/script?v=2"',
        "Framer analytics beacon -> disabled",
    )
    patch_file(
        "index.html",
        'data-no-nt></script>',
        "data-no-nt></script>\n    -->",
        "Framer analytics beacon -> close comment",
    )


def main() -> int:
    # url -> local rel path, for every asset we successfully stored
    mapping: dict[str, str] = {}
    # rel path -> raw bytes, for text assets we still need to rewrite
    text_bodies: dict[str, bytes] = {}
    failed: list[tuple[str, str]] = []

    print("→ fetching entry document", SITE)
    index_html = fetch(SITE)
    text_bodies["index.html"] = index_html

    queue: deque[str] = deque()
    seen: set[str] = set()

    def enqueue_from(blob: bytes, base_url: str | None) -> None:
        text = blob.decode("utf-8", "replace")
        for m in URL_RE.finditer(text):
            u = m.group(0).rstrip("\\\"'),;")
            if u not in seen:
                seen.add(u)
                queue.append(u)
        # Relative ESM imports resolve against the chunk's own directory.
        if base_url:
            base_dir = base_url.rsplit("/", 1)[0]
            for m in REL_MJS_RE.finditer(text):
                u = base_dir + "/" + m.group(1)[2:]
                if u not in seen:
                    seen.add(u)
                    queue.append(u)

    enqueue_from(index_html, None)

    while queue:
        url = queue.popleft()
        # Chunks also contain bare directory prefixes that get concatenated
        # at runtime (e.g. the fontshare CDN base). Those are not assets.
        if url.endswith("/") or not os.path.basename(urlsplit(url).path):
            continue
        rel = local_path(url)
        dest = os.path.join(OUT, rel)
        try:
            body = fetch(url)
        except urllib.error.HTTPError as e:
            failed.append((url, f"HTTP {e.code}"))
            continue
        except Exception as e:  # noqa: BLE001 - report and keep mirroring
            failed.append((url, type(e).__name__))
            continue

        mapping[url] = rel
        if is_text(rel):
            text_bodies[rel] = body
            enqueue_from(body, url)
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(body)
        print(f"  {len(mapping):3d}  {rel}")

    # Rewrite every absolute reference to a *document-relative* local path
    # ("assets/..." rather than "/assets/..."), so the site works both at a
    # domain root and under a subpath like user.github.io/repo/. Framer resolves
    # asset strings with `new URL(value, document.baseURI)`, and the only CSS is
    # inline in index.html, so document-relative is correct everywhere here.
    #
    # Longest URL first so that foo.png?scale-down-to=512 is replaced
    # before the shorter foo.png prefix can match it.
    order = sorted(mapping, key=len, reverse=True)
    rewrites = 0
    for rel, body in text_bodies.items():
        text = body.decode("utf-8", "replace")
        for url in order:
            if url in text:
                text = text.replace(url, mapping[url])
                rewrites += 1
        # Relative chunk imports keep working because chunks stay siblings
        # under assets/framer/, so no rewriting is needed for those.
        dest = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(text)

    # Root-level files that aren't reachable from the document graph.
    for name in ("robots.txt", "sitemap.xml"):
        try:
            body = fetch(SITE + name)
        except Exception as e:  # noqa: BLE001
            print(f"  ! {name}: {type(e).__name__}")
            continue
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(body)
        print(f"  {name}")

    # Marker for branch-based GitHub Pages serving, where Jekyll would
    # otherwise drop any underscore-prefixed path. The Actions deploy path
    # ignores Jekyll already, but this keeps both options safe.
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    apply_selfhost_patches()

    print(f"\n✓ {len(mapping)} assets, {len(text_bodies)} text files, {rewrites} rewrites")
    if failed:
        print(f"\n✗ {len(failed)} failed:")
        for url, why in failed:
            print(f"   {why}  {url}")

    with open(os.path.join(ROOT, "tools", "manifest.json"), "w") as f:
        json.dump(
            {"site": SITE, "assets": mapping, "failed": failed},
            f, indent=2, sort_keys=True,
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
