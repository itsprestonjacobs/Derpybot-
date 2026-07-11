# The course website (`docs/`)

`index.html` is the **entire course as one standalone website** — sidebar navigation, one
lesson at a time, progress tracking, copy buttons, and a light/dark toggle. It's a single
self-contained file with no external dependencies, so it works anywhere you can host a
static page.

GitHub Pages is set to serve **this folder**, so `index.html` here is what students see.

## Preview it locally

Double-click `index.html` — it opens in your browser. No server needed.

## Turn on GitHub Pages (one time)

1. On the repo, go to **Settings → Pages**.
2. Under **Build and deployment → Source**, choose **Deploy from a branch**.
3. Pick the `main` branch and the **`/docs`** folder, then **Save**.
4. Wait a minute and refresh — GitHub shows your live URL, like
   `https://itsprestonjacobs.github.io/Course/`.

That link is your published course. Every time you push a change to `docs/`, the site
updates automatically.

## Rebranding

The accent color, studio name, and logo letter are set in `tools/build.py`
(`TOKENS_LIGHT` / `TOKENS_DARK` for colors, and the course-name/logo text).
Change them, run `python tools/build.py`, and push. To edit lesson **content**, edit the
markdown in `course/` and rerun the build — this file is regenerated from it.

> Don't hand-edit `index.html` directly — it's generated, so your changes would be
> overwritten on the next build. Edit `course/` and `tools/build.py` instead.
