# orgscale.ai

Marketing site for **Orgscale** — a tool that measures how well a company's
people are aligned with its vision. Leadership answers a short scan, and
Orgscale reports where roles, goals and assumptions have drifted out of sync,
before the drift turns into cost.

This repository is the public landing page. The product itself lives separately
at [chat.orgscale.ai](http://chat.orgscale.ai/), which is where every
**Get Started** link points.

## Running locally

```bash
npm start
```

Opens on <http://localhost:4321>. A static server is included because the page
loads fonts and SVGs over HTTP; opening `index.html` straight off disk will not
resolve them.

## Structure

```
index.html          the page
css/styles.css      design tokens + layout
js/main.js          scroll reveals
assets/fonts/       Manrope (variable), Lora
assets/img/         photography and rendered art
assets/svg/         logo, icons, line work
```

Plain HTML, CSS and a little vanilla JavaScript — no build step, no framework,
no dependencies. Editing the site means editing these files.

## Deployment

Pushing to `main` publishes the site through GitHub Pages.
