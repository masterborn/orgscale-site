# orgscale.ai — self-hosted static copy

A fully self-contained reproduction of the `orgscale.ai` landing page. Nothing
is loaded from `framerusercontent.com` or `fonts.gstatic.com` at runtime: all
111 assets (fonts, images, JS chunks) are served from `public/`.

The original is a Framer site, so this copy keeps Framer's server-rendered
markup and its client runtime. That is what makes the animations, scroll
reveals, breakpoints and hover states behave identically rather than
approximately — it is the same code, pointed at local assets.

## Run it

```bash
npm start
```

Then open <http://localhost:4321>.

A static server is required — the page hydrates via native ES modules, which
browsers refuse to load over `file://`. `server.js` has no dependencies; it
exists mainly to serve `.mjs` as `text/javascript`, which `python3 -m
http.server` gets wrong.

## Layout

```
.github/workflows/      # GitHub Pages deploy
public/                 # the deployable web root
  index.html
  robots.txt
  sitemap.xml
  .nojekyll
  assets/
    framer/             # Framer runtime chunks (ESM) + the page bundle
    fonts/{google,fontshare,framer}/
    images/
server.js               # zero-dep static server
tools/mirror.py         # re-downloads and re-localizes everything
tools/manifest.json     # every source URL -> its local path
```

## Re-syncing after the Framer site changes

```bash
npm run mirror
```

`tools/mirror.py` walks the dependency graph from the live document: it
downloads each `framerusercontent.com` / `fonts.gstatic.com` asset, rewrites
every reference to a local root-relative path, and re-scans text assets so
lazily imported font chunks are picked up too. It rewrites longest-URL-first,
so `image.png?scale-down-to=512` is localized as its own file rather than being
clobbered by the shorter `image.png` prefix.

Note that Framer's bundle filenames are content-hashed, so a redeploy of the
Framer site changes them. Re-running the mirror handles that; hand-editing the
chunks does not survive it.

## Verified against production

Compared with headless Chromium at every Framer breakpoint (`>=1440`,
`810–1439`, `<=809`), after scrolling the full page so all scroll-reveal
animations fire.

| Viewport | Pixel diff vs live | Page height | Body text | Computed styles |
|---|---|---|---|---|
| 1512 | 0.0000% | identical | identical | 0 diffs / 81 nodes |
| 1440 | 0.0000% | identical | identical | 0 diffs / 81 nodes |
| 1200 | 0.0000% | identical | identical | 0 diffs / 80 nodes |
| 810  | 0.0403% | identical | identical | 0 diffs / 80 nodes |
| 500  | 0.0139% | identical | identical | 0 diffs / 61 nodes |
| 390  | 0.0221% | identical | identical | 0 diffs / 61 nodes |

The computed-style check samples font family, size, weight, line-height,
letter-spacing, color, margins, padding and box dimensions on every heading,
paragraph, link, button and list item — the places a rebuilt clone drifts even
when a screenshot looks right. All identical.

The residual pixels are the page's own animation frame-timing jitter, not a
defect in the copy. Control run, capturing the **live site twice** and diffing
it against itself:

| Viewport | live vs live | live vs local |
|---|---|---|
| 1512 | 0.0016% | 0.0019% |
| 810  | 0.0406% | 0.0000% |
| 390  | 0.0009% | 0.0230% |

The site differs from itself by as much as it differs from this copy — at 810px
the copy was 2 pixels off production, less than production's own run-to-run
variance.

Also checked to match: all 6 `Get Started` links, the `#problem` / `#solution`
/ `#report` anchors (identical scroll offset, 2436px), every image loading, and
zero failed asset requests locally.

## Intentional differences from production

Three, none of them visual.

1. **`chat.orgscale.ai` stays external.** All 6 `Get Started` links still point
   at `http://chat.orgscale.ai/`, unchanged, since the chat is a separate app.
   They are plain `http://` in the original — worth switching to `https://` in
   Framer.
2. **Framer's analytics beacon (`events.framer.com`) is commented out** in
   `index.html`. It is keyed by `data-fid` to the Framer-hosted deployment.
3. **Framer's editor bar is stubbed** (`assets/framer/editor-bar-stub.mjs`)
   instead of importing `https://edit.framer.com/init.mjs`. That import is
   already CORS-blocked on production, so it never renders there either; the
   stub just removes the console error.

Both 2 and 3 are applied by `tools/mirror.py`, so re-mirroring keeps them.

## Known issues inherited from production

- **`index.html` contains a broken inline script** (in Framer's `headEnd`
  injection): a stray `,` before `calculateRealTime();` makes it throw
  `SyntaxError: Unexpected token ','`. It also runs in `<head>` and queries
  `#input1`–`#input4` / `#resultText`, none of which exist on the page. It
  throws identically on the live site and does nothing there either. Kept
  verbatim; fix it in Framer, not here.
- **Google Analytics (`G-E6B0PYL8QG`) is kept as-is**, so running this locally
  or on a staging host sends `page_view` hits to the same property as
  production. Gate it by hostname if that matters.

## Deploying to GitHub Pages

`.github/workflows/pages.yml` deploys `public/` on every push to `main`. One
setup step in the repo: **Settings → Pages → Source → GitHub Actions**. No
other service is involved.

Asset paths are **document-relative**, so the same build works unmodified both
at a domain root and under a project subpath like
`masterborn.github.io/orgscale-site/`.

Re-running the full comparison against the **deployed** Pages site gave
0.0000% at 1512, 1440 and 390, and ≤0.0003% at 810 and 500, with identical text
and zero computed-style diffs throughout. At 1200 the figure moves between
0.50% and 1.06% run to run — a section there animates a fanning-line graphic
whose progress depends on frame timing. A live-vs-live control at that same
viewport measured **1.37%**, i.e. production differs from itself more than it
differs from this copy, and the deployed site served zero failed requests.

Why Actions rather than pointing Pages at a folder: Pages' branch-based source
only offers the repo root or `/docs`, not `/public`, and it runs Jekyll, which
silently drops underscore-prefixed paths. The Actions path uploads the
directory as-is. (`public/.nojekyll` is committed anyway, so switching to
branch-based serving stays safe. If you prefer that route, rename `public/` to
`docs/` and set Source → Deploy from a branch → `/docs`.)

Live at **<https://masterborn.github.io/orgscale-site/>**.

### MIME types on Pages — confirmed

GitHub Pages serves everything this site needs with the right `Content-Type`,
measured against the actual deployment:

| Path | Content-Type |
|---|---|
| `/` | `text/html; charset=utf-8` |
| `assets/framer/*.mjs` | `text/javascript; charset=utf-8` |
| `assets/fonts/**/*.woff2` | `font/woff2` |
| `assets/images/*.webp` | `image/webp` |

`.mjs` was the risk — browsers refuse to execute a module served as
`application/octet-stream`, which would break hydration entirely. Pages gets it
right, so no `.mjs` → `.js` renaming is needed.

### Custom domain

Serving this on `orgscale.ai` itself means moving the domain's DNS off Framer,
at which point this copy *becomes* the site. Add a `CNAME` file to `public/`
(and to `tools/mirror.py`, so re-mirroring keeps it).

Until then, `robots.txt`, `sitemap.xml` and the `og:`/`canonical` meta tags
still say `https://orgscale.ai/`. That is the right setup for a staging deploy —
the `canonical` tag tells search engines the Framer original is the real page,
so the `github.io` copy should not compete with it. It becomes wrong the moment
this copy is meant to *be* the site.

Note that the repo is public, so this copy is world-readable and crawlable. If
you would rather it were not indexed at all while it is staging, change
`public/robots.txt` to `Disallow: /` — but that is a deliberate deviation from
production, so it is not applied by default.
