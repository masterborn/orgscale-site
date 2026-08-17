#!/usr/bin/env node
/**
 * Zero-dependency static server for ./public.
 *
 * A plain `python3 -m http.server` is not enough here: the page hydrates via
 * native ES modules, and browsers reject a module served with the wrong
 * Content-Type. So .mjs must be text/javascript.
 */

const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "public");
const PORT = Number(process.env.PORT) || 4321;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".woff": "font/woff",
  ".ttf": "font/ttf",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".txt": "text/plain; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
};

http
  .createServer((req, res) => {
    let pathname;
    try {
      pathname = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
    } catch {
      res.writeHead(400).end("Bad Request");
      return;
    }

    // Resolve inside ROOT only, so no ../ can escape the web root.
    let file = path.join(ROOT, pathname);
    if (!file.startsWith(ROOT)) {
      res.writeHead(403).end("Forbidden");
      return;
    }
    if (pathname.endsWith("/")) file = path.join(file, "index.html");

    fs.stat(file, (err, st) => {
      if (!err && st.isDirectory()) file = path.join(file, "index.html");
      fs.readFile(file, (err2, body) => {
        if (err2) {
          // Single-page site: unknown paths fall back to the document,
          // which keeps deep links and #anchors working.
          fs.readFile(path.join(ROOT, "index.html"), (err3, fallback) => {
            if (err3) {
              res.writeHead(404, { "Content-Type": "text/plain" }).end("Not Found");
            } else {
              res.writeHead(200, { "Content-Type": MIME[".html"] }).end(fallback);
            }
          });
          return;
        }
        const type = MIME[path.extname(file).toLowerCase()] || "application/octet-stream";
        res.writeHead(200, { "Content-Type": type, "Cache-Control": "no-cache" }).end(body);
      });
    });
  })
  .listen(PORT, () => {
    console.log(`orgscale mirror → http://localhost:${PORT}`);
  });
