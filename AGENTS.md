# AGENTS.md — xiaobin83.github.io

Jekyll-based GitHub Pages site (theme: minima). Hosting instructions for AI agents.

## Host the project

```bash
cd /home/xiaobin/Workspace/xiaobin83.github.io

# Kill any existing server
fuser -k 9090/tcp

# Start Jekyll (bind 0.0.0.0 for WSL2 → Windows browser access)
bundle exec jekyll serve --port 9090 --host 0.0.0.0 --no-watch &

# If gems are missing, install first:
bundle install
```

Gems are installed to `vendor/bundle/` locally (no sudo needed).

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
