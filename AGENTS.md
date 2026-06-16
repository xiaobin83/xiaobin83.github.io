# AGENTS.md — xiaobin83.github.io

Jekyll-based GitHub Pages site (theme: minima). Hosting instructions for AI agents.

## Host the project

### Option A: Ruby/Jekyll available (preferred)

```bash
cd /home/xiaobin/Workspace/xiaobin83.github.io
bundle install
bundle exec jekyll serve --port 9090
```

### Option B: No Ruby/Jekyll (fallback)

Use the custom build script and Python HTTP server:

```bash
cd /home/xiaobin/Workspace/xiaobin83.github.io

# 1. Build (Jekyll-like render: md→HTML via _layouts/)
python3 build.py

# 2. Serve
python3 -m http.server 9090 --directory _site &

# 3. Kill server when done
fuser -k 9090/tcp
```

### Build script details

`build.py` — A minimal Jekyll renderer:
- Parses YAML front matter
- Converts markdown to HTML (custom converter — does NOT handle Liquid `{% %}` tags)
- Applies layout chain (`_layouts/*.html`)
- Outputs to `_site/`
- Static files (HTML, CSS) from `understanding-omo/`, `docs/` are copied as-is
- `_posts/` are skipped (Liquid tag incompatibility)

`_layouts/`:
- `default.html` — Full HTML skeleton with solarized-light theme
- `home.html` — Home page (wraps content in default)
- `page.html` — Generic page (wraps content with `<h1>` title, chains to default)

## Site structure

```
_config.yml          # Jekyll config (theme: minima, title: "0x600d1dea")
index.md             # Home page (layout: home) — Architecture Documents links
about.md             # About page (layout: page)
understanding-omo/   # Oh My OpenAgent guide (static HTML + CSS)
docs/                # Vikingbot architecture docs (static HTML)
```

## Key URLs (when served)

| Page | Path |
|------|------|
| Home | `/` |
| About | `/about/` |
| OpenAgent Guide | `/understanding-omo/guide.html` |
| Vikingbot Architecture | `/docs/vikingbot-architecture.html` |
| Agent Memory | `/docs/agent-memory-architecture.html` |

## Notes

- No `_site/` directory in git (Jekyll's standard `.gitignore` applies)
- Default port: `9090`
- Kill existing server before starting: `fuser -k 9090/tcp`
