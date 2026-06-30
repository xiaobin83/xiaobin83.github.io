# AGENTS.md — xiaobin83.github.io

Jekyll + custom Python builder site. Hosting instructions & writing style guide for AI agents.

## Host the project

```bash
cd /path/to/xiaobin83.github.io

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
build.py             # Custom static site builder (processes .md + copies static files)
_layouts/            # Layout templates (default.html, home.html, page.html)
assets/main.css      # Central theme with dark/light CSS custom properties
docs/understanding-omo/   # Oh My OpenAgent guide (static HTML + CSS)
docs/                # Vikingbot architecture docs (static HTML)
```

## Key URLs (when served)

| Page | Path |
|------|------|
| Home | `/` |
| About | `/about/` |
| OpenAgent Guide | `/docs/understanding-omo/guide.html` |
| Vikingbot Architecture | `/docs/vikingbot-architecture.html` |
| Agent Memory | `/docs/agent-memory-architecture.html` |

## Writing Style Guide

### Tone & Voice
- **Technical but warm**: Explain complex architecture in plain terms. Use metaphors, diagrams (ASCII), and real examples. Avoid dry academic tone.
- **Light-hearted where appropriate**: The author tagline says "Game Developer 🎮 | Vibe Coder 🖥️ | Amateur Boxer 🥊 | Permanent Vacation Retirement 🌴". Let some personality through — slight playfulness in section headers, emoji in diagrams, conversational asides in parentheses.
- **Chinese docs** (understanding-omo): Write in zh-CN. Keep it beginner-friendly for technical readers new to the framework.
- **Architecture docs** (vikingbot, agent-memory): Chinese body text with English code/symbol references. Deep technical depth — assume reader knows programming but not the framework internals.

### Formatting
- Use semantic headers (`h1` title, `h2` sections, `h3` subsections). Keep hierarchy clean.
- Code blocks must specify a language tag (`python`, `yaml`, `typescript`, `bash`).
- Tables for structured comparisons (features, configs, APIs).
- Prefer `pre` + inline spans over `<span>` tags for syntax highlighting in architecture docs.
- Bullet lists for unordered items, numbered lists for sequential steps.
- `blockquote` for key insights or summary callouts.
- Descriptive link text, not bare URLs. Use relative paths for internal links.

### Structure (Architecture Docs)
Each deep-dive should follow this pattern:
1. **Hero section**: Title, one-liner, badge/tag cloud
2. **TOC**: Numbered table of contents (2-column grid)
3. **Layered breakdown**: Start from user-facing, go deep. Each layer = a `section`.
4. **Cards**: Use `.card` for grouped concepts, `.two-col`/`.grid-2` for side-by-side comparison
5. **Flow diagrams**: Use `.flow-box` with monospace, `span.hl` for keywords, `span.dim` for comments
6. **End-to-end data flow**: ASCII art or step-by-step flow showing complete pipeline
7. **Design highlights**: Summary card grid of design principles

### Theme & Assets
- All pages support **dark/light mode** via `data-theme` on `<html>`. Never hardcode colors — use CSS custom properties.
- Font stack: `Inter` for body, `JetBrains Mono` for code. No serif fonts.
- Run `python3 build.py` after any content change, then serve via `python3 -m http.server 9090 --directory _site`.

## Notes

- No `_site/` directory in git (Jekyll's standard `.gitignore` applies)
- Default port: `9090`
- Kill existing server before starting: `fuser -k 9090/tcp`
