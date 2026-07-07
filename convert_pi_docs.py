#!/usr/bin/env python3
"""
Convert pi-docs/*.md to docs/understanding-pi/*.html
Style matches docs/understanding-omo/ (shared style.css, nav sidebar, section-based layout).
"""

import re
import os
import html as html_lib
import markdown

SRC_DIR = "pi-docs"
OUT_DIR = "docs/understanding-pi"

# ── Page metadata ──────────────────────────────────────────────
# (source_path, output_filename, nav_title, page_title, nav_section)
PAGES = [
    ("README.md",                    "index.html",                "首页",         "Pi 文档首页",         "overview"),
    ("architecture.md",              "architecture.html",         "整体架构",      "Pi 整体架构",          "overview"),
    ("data-flow.md",                 "data-flow.html",            "数据流",        "Pi 数据流",            "overview"),
    ("packages/pi-ai.md",              "pi-ai.html",                "pi-ai",        "pi-ai 包设计",        "packages"),
    ("packages/pi-agent-core.md",      "pi-agent-core.html",        "pi-agent-core","pi-agent-core 包设计","packages"),
    ("packages/pi-coding-agent.md",     "pi-coding-agent.html",      "pi-coding-agent","pi-coding-agent 包设计","packages"),
    ("packages/pi-tui.md",             "pi-tui.html",               "pi-tui",       "pi-tui 包设计",       "packages"),
    ("packages/pi-orchestrator.md",     "pi-orchestrator.html",      "pi-orchestrator","pi-orchestrator 包设计","packages"),
    ("extension-system.md",          "extension-system.html",     "扩展系统",      "Pi 扩展系统",          "system"),
    ("session-and-compaction.md",    "session-and-compaction.html","会话与压缩",    "Pi 会话与压缩",        "system"),
    ("build-and-release.md",         "build-and-release.html",    "构建与发布",    "Pi 构建与发布",        "system"),
    ("contributing.md",              "contributing.html",         "贡献指南",      "Pi 贡献指南",          "system"),
]

# Map source filename → output filename for link conversion
SRC_TO_OUT = {}
for src, out, _, _, _ in PAGES:
    # Handle packages/ prefix
    base = src
    SRC_TO_OUT[base + ")"] = out + ")"
    SRC_TO_OUT[base] = out

# Nav groups (title, list of (output_filename, nav_title))
NAV_GROUPS = [
    ("架构概览", [
        ("index.html",         "首页"),
        ("architecture.html",  "整体架构"),
        ("data-flow.html",     "数据流"),
    ]),
    ("包设计", [
        ("pi-ai.html",             "pi-ai"),
        ("pi-agent-core.html",     "pi-agent-core"),
        ("pi-coding-agent.html",   "pi-coding-agent"),
        ("pi-tui.html",            "pi-tui"),
        ("pi-orchestrator.html",   "pi-orchestrator"),
    ]),
    ("系统机制", [
        ("extension-system.html",          "扩展系统"),
        ("session-and-compaction.html",    "会话与压缩"),
        ("build-and-release.html",         "构建与发布"),
        ("contributing.html",              "贡献指南"),
    ]),
]


def slugify(text: str) -> str:
    """Generate URL-safe slug from heading text."""
    # Remove markdown formatting
    clean = re.sub(r'[`*_~]', '', text)
    # For Chinese text, use a hash-based id to ensure uniqueness and validity
    import hashlib
    h = hashlib.md5(clean.encode()).hexdigest()[:8]
    # Try to make a readable slug for ASCII parts
    ascii_part = re.sub(r'[^a-zA-Z0-9]+', '-', clean).strip('-').lower()
    if ascii_part:
        return f"{ascii_part}-{h}"[:60]
    return f"sec-{h}"


def convert_internal_links(md_text: str) -> str:
    """Convert internal .md links to .html links."""
    # Match markdown links: [text](path.md) but not [text](../external/path.md)
    # Only convert links to files within pi-docs (no ../ prefix)
    def replace_link(m):
        full = m.group(0)
        link_text = m.group(1)
        url = m.group(2)
        # Skip external URLs and relative-up paths
        if url.startswith(('http://', 'https://', '../', '#', 'mailto:')):
            return full
        # Convert .md to .html for internal links
        if url.endswith('.md'):
            # Extract filename without path
            filename = os.path.basename(url)
            # Find matching output filename
            for src, out, _, _, _ in PAGES:
                if os.path.basename(src) == filename:
                    return f'[{link_text}]({out})'
        return full

    return re.sub(r'\[([^\]]*)\]\(([^)]+)\)', replace_link, md_text)


def markdown_to_sections(md_text: str):
    """
    Convert markdown to list of (id, title, html_content) sections.
    Splits on h2 (##). First section (before any h2) contains h1.
    Returns list of (section_id, section_title_for_toc, inner_html).
    """
    # Convert internal links first
    md_text = convert_internal_links(md_text)

    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'nl2br'],
        extension_configs={
            'fenced_code': {},
        }
    )

    # Remove <br /> from inside <pre> blocks (nl2br adds them, but we don't want them in code)
    def fix_pre_br(match):
        content = match.group(1)
        content = content.replace('<br />', '\n').replace('<br/>', '\n')
        return f'<pre>{content}</pre>'
    # This regex handles <pre>...</pre> blocks (non-greedy)
    html_body = re.sub(r'<pre>(.*?)</pre>', fix_pre_br, html_body, flags=re.DOTALL)

    # Also fix <br /> inside <table> (nl2br shouldn't add br in tables but just in case)
    # Actually, let's just not use nl2br and handle newlines differently
    # Re-convert without nl2br
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code'],
    )

    # Split into sections by <h2>
    h1_match = re.search(r'<h1>(.*?)</h1>', html_body, re.DOTALL)
    h1_text = h1_match.group(1).strip() if h1_match else "Pi"

    parts = re.split(r'(<h2>.*?</h2>)', html_body, flags=re.DOTALL)

    sections = []

    intro_html = parts[0].strip()
    if intro_html:
        sections.append(("hero", h1_text, intro_html, h1_text))

    # Process h2 sections
    i = 1
    while i < len(parts):
        h2_tag = parts[i]
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""

        # Extract h2 text
        h2_text_match = re.search(r'<h2>(.*?)</h2>', h2_tag, re.DOTALL)
        h2_text = h2_text_match.group(1).strip() if h2_text_match else ""
        h2_clean = re.sub(r'<[^>]+>', '', h2_text)  # Remove any HTML tags inside

        section_id = slugify(h2_clean)

        # Add id to the h2 tag
        h2_with_id = f'<h2 id="{section_id}">{h2_text}</h2>'

        sections.append((section_id, h2_clean, h2_with_id + "\n" + content, h2_clean))
        i += 2

    return h1_text, sections


def build_toc(sections):
    """Build TOC items from sections (skip the intro/hero section)."""
    items = []
    for sec_id, sec_title, _, toc_title in sections:
        # Skip intro section in TOC (it's the h1 page title)
        if sec_id == "hero":
            continue
        items.append(f'      <li><a href="#{sec_id}">{html_lib.escape(toc_title)}</a></li>')
    return "\n".join(items)


def build_nav(current_output: str, sections):
    """Build the full nav sidebar HTML."""
    toc_html = build_toc(sections)

    nav_sections = []

    # Back link
    nav_sections.append(f"""  <div class="nav-section">
    <div class="nav-title">导航</div>
    <ul>
      <li class="nav-back"><a href="index.html">← 返回首页</a></li>
    </ul>
  </div>""")

    # Document groups
    for group_title, pages in NAV_GROUPS:
        items = []
        for out_file, nav_title in pages:
            cls = ' class="current"' if out_file == current_output else ""
            items.append(f'      <li><a{cls} href="{out_file}">{nav_title}</a></li>')
        nav_sections.append(f"""  <div class="nav-section">
    <div class="nav-title">{group_title}</div>
    <ul>
{chr(10).join(items)}
    </ul>
  </div>""")

    # Per-page TOC
    if toc_html:
        nav_sections.append(f"""  <div class="nav-section">
    <div class="nav-title">本页目录</div>
    <ul>
{toc_html}
    </ul>
  </div>""")

    nav_inner = "\n\n".join(nav_sections)

    # Find current page's nav_title for the version display
    version_text = ""
    for src, out, nav_title, page_title, _ in PAGES:
        if out == current_output:
            version_text = nav_title
            break

    return f"""<nav>
  <div class="menu-toggle" onclick="this.parentElement.classList.toggle('open')"><span></span><span></span><span></span></div>
  <div class="logo">Pi</div>
  <div class="version">{html_lib.escape(version_text)}</div>

{nav_inner}
</nav>"""


def build_sections_html(sections):
    """Build <section> blocks from parsed sections."""
    html_parts = []
    for sec_id, sec_title, inner_html, toc_title in sections:
        html_parts.append(f'<section id="{sec_id}">\n{inner_html}\n</section>')
    return "\n\n".join(html_parts)


def build_prev_next(current_idx):
    """Build prev/next navigation."""
    prev_link = ""
    next_link = ""

    if current_idx > 0:
        prev_src, prev_out, prev_nav, prev_title, _ = PAGES[current_idx - 1]
        prev_link = f'<a class="prev" href="{prev_out}">← {html_lib.escape(prev_nav)}</a>'

    if current_idx < len(PAGES) - 1:
        next_src, next_out, next_nav, next_title, _ = PAGES[current_idx + 1]
        next_link = f'<a class="next" href="{next_out}">{html_lib.escape(next_nav)} →</a>'

    return f"""<div class="next-section">
  {prev_link}
  {next_link}
</div>"""


def convert_page(src_path, out_file, page_title, current_idx):
    """Convert a single markdown page to HTML."""
    # Read markdown
    full_src = os.path.join(SRC_DIR, src_path)
    if not os.path.exists(full_src):
        print(f"  SKIP: {full_src} not found")
        return False

    with open(full_src, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert to sections
    h1_text, sections = markdown_to_sections(md_text)

    # Build nav
    nav_html = build_nav(out_file, sections)

    # Build sections HTML
    sections_html = build_sections_html(sections)

    # Build prev/next
    prev_next_html = build_prev_next(current_idx)

    # Assemble full HTML
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_lib.escape(page_title)} — Pi</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

{nav_html}

<main>

{sections_html}

{prev_next_html}
</main>
</body>
</html>
"""

    # Write output
    out_path = os.path.join(OUT_DIR, out_file)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"  OK: {out_path} ({len(full_html)} bytes)")
    return True


def main():
    print(f"Converting {len(PAGES)} markdown files to HTML...")
    print(f"  Source: {SRC_DIR}/")
    print(f"  Output: {OUT_DIR}/")
    print()

    success = 0
    for i, (src, out, nav_title, page_title, group) in enumerate(PAGES):
        print(f"[{i+1}/{len(PAGES)}] {src} → {out}")
        if convert_page(src, out, page_title, i):
            success += 1

    print()
    print(f"Done: {success}/{len(PAGES)} pages converted.")
    print(f"Output directory: {OUT_DIR}/")


if __name__ == "__main__":
    main()
