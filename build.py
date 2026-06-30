#!/usr/bin/env python3
"""Minimal Jekyll-style static site builder for this project."""

import re
import os
import yaml
import shutil
from datetime import datetime

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(SITE_DIR, "_site")
SITE_CONFIG = {
    "title": "0x600d1dea",
    "email": "xiaobin.huang@gmail.com",
    "description": "Personal site — architecture deep dives, Oh My OpenAgent guides, and AI agent framework notes by xiaobin83.",
    "baseurl": "",
    "url": "",
    "github_username": "xiaobin83",
}

def parse_front_matter(text):
    """Parse YAML front matter from markdown text. Returns (dict, content_str)."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            content = parts[2].strip()
            return fm, content
    return {}, text.strip()

def md_to_html(text):
    """Convert basic markdown to HTML."""
    lines = text.split("\n")
    result = []
    i = 0
    in_code_block = False
    
    while i < len(lines):
        line = lines[i]
        
        # Code blocks
        if line.startswith("```"):
            if in_code_block:
                result.append("</code></pre>")
                in_code_block = False
            else:
                result.append('<pre><code>')
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            result.append(line)
            i += 1
            continue
        
        # Headings
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            level = len(m.group(1))
            result.append(f"<h{level}>{m.group(2)}</h{level}>")
            i += 1
            continue
        
        # Horizontal rule
        if re.match(r"^[-*_]{3,}\s*$", line):
            result.append("<hr>")
            i += 1
            continue
        
        # Unordered lists - collect consecutive items
        if re.match(r"^[-*+]\s+", line):
            result.append("<ul>")
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                item_text = re.sub(r"^[-*+]\s+", "", lines[i])
                result.append(f"<li>{inline_md(item_text)}</li>")
                i += 1
            result.append("</ul>")
            continue
        
        # Ordered lists
        if re.match(r"^\d+\.\s+", line):
            result.append("<ol>")
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\d+\.\s+", "", lines[i])
                result.append(f"<li>{inline_md(item_text)}</li>")
                i += 1
            result.append("</ol>")
            continue
        
        # Blockquote
        if line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:])
                i += 1
            result.append(f"<blockquote>{'<br>'.join(inline_md(l) for l in quote_lines)}</blockquote>")
            continue
        
        # Tables
        if "|" in line and i + 1 < len(lines) and re.match(r"^\|?[\s\-:|]+\|?$", lines[i+1]):
            result.append("<table>")
            # Header
            headers = [c.strip() for c in line.split("|") if c.strip()]
            result.append("<thead><tr>" + "".join(f"<th>{inline_md(h)}</th>" for h in headers) + "</tr></thead>")
            i += 2  # Skip separator
            result.append("<tbody>")
            while i < len(lines) and "|" in lines[i]:
                cells = [c.strip() for c in lines[i].split("|") if c.strip()]
                result.append("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in cells) + "</tr>")
                i += 1
            result.append("</tbody></table>")
            continue
        
        # Paragraph (non-empty, non-special)
        if line.strip():
            # Collect consecutive paragraph lines
            para_lines = []
            while i < len(lines) and lines[i].strip() and not any(
                lines[i].startswith(p) for p in ["#", "- ", "* ", "+ ", "> ", "```", "|"]
            ) and not re.match(r"^\d+\.\s+", lines[i]):
                para_lines.append(lines[i])
                i += 1
            result.append(f"<p>{' '.join(inline_md(l) for l in para_lines)}</p>")
            continue
        
        # Empty line
        i += 1
    
    return "\n".join(result)

def inline_md(text):
    """Convert inline markdown: **bold**, *italic*, `code`, [links](url), ![alt](url)."""
    # Images
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text

def resolve_layout(layout_name, page_vars, content_html):
    layout_path = os.path.join(SITE_DIR, "_layouts", f"{layout_name}.html")
    if not os.path.exists(layout_path):
        return apply_template_vars(content_html, page_vars)
    
    with open(layout_path, "r") as f:
        layout_src = f.read()
    
    layout_fm = {}
    if layout_src.startswith("---"):
        parts = layout_src.split("---", 2)
        if len(parts) >= 3:
            layout_fm = yaml.safe_load(parts[1]) or {}
            layout_body = parts[2]
        else:
            layout_body = layout_src
    else:
        layout_body = layout_src
    
    this_result = layout_body.replace("{{ content }}", content_html)
    
    if "layout" in layout_fm:
        return resolve_layout(layout_fm["layout"], page_vars, this_result)
    
    return apply_template_vars(this_result, page_vars)

def apply_template_vars(result, page_vars):
    for key, val in SITE_CONFIG.items():
        result = result.replace(f"{{{{ site.{key} }}}}", str(val))
    for key, val in page_vars.items():
        result = result.replace(f"{{{{ page.{key} }}}}", str(val))
    result = re.sub(
        r"\{\{\s*['\"]now['\"]\s*\|\s*date:\s*['\"](%[YymdHMS]+)['\"]\s*\}\}",
        lambda m: datetime.now().strftime(m.group(1)),
        result
    )
    result = re.sub(
        r"\{\{\s*['\"](/[^'\"]+)['\"]\s*\|\s*relative_url\s*\}\}",
        lambda m: f"{SITE_CONFIG['baseurl']}{m.group(1)}",
        result
    )
    return result

def inject_docs_theme(file_path):
    with open(file_path, 'r') as f:
        html = f.read()
    if 'data-omo-docs="1"' in html:
        return
    is_omo = '/understanding-omo/' in file_path
    font_html = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'
    )
    head_script = (
        '<script>\n'
        '(function() {\n'
        '  var m = document.cookie.match(/(?:^| )theme=([^;]*)/);\n'
        '  document.documentElement.setAttribute("data-theme", m ? m[1] : (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));\n'
        '})();\n'
        '</script>'
    )
    html = html.replace('</head>', font_html + '\n' + head_script + '\n</head>')
    if not is_omo:
        html = html.replace('</head>', '<link rel="stylesheet" href="/assets/main.css">\n</head>')
    sun_svg = '<svg class="icon-sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
    moon_svg = '<svg class="icon-moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
    toggle_button = (
        '<button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle dark mode">\n'
        '      ' + sun_svg + '\n'
        '      ' + moon_svg + '\n'
        '    </button>'
    )
    toggle_script = (
        '<script>\n'
        'function toggleTheme() {\n'
        '  var html = document.documentElement;\n'
        '  var current = html.getAttribute("data-theme");\n'
        '  var next = current === "dark" ? "light" : "dark";\n'
        '  html.setAttribute("data-theme", next);\n'
        '  document.cookie = "theme=" + next + ";path=/;max-age=31536000";\n'
        '}\n'
        '</script>'
    )
    if is_omo:
        header = (
            '<header class="doc-topbar">\n'
            '  <a class="doc-topbar-title" href="/">0x600d1dea</a>\n'
            '  ' + toggle_button + '\n'
            '</header>\n'
            '<div class="body-wrap">'
        )
        html = html.replace('<body>', '<body data-omo-docs="1">\n' + header)
        html = html.replace('</body>', '</div>\n' + toggle_script + '\n</body>')
    else:
        header = (
            '<header class="site-header" role="banner">\n'
            '  <div class="wrapper header-inner">\n'
            '    <a class="site-title" href="/">0x600d1dea</a>\n'
            '    ' + toggle_button + '\n'
            '  </div>\n'
            '</header>'
        )
        html = html.replace('<body>', '<body data-omo-docs="1">\n' + header)
        html = html.replace('</body>', toggle_script + '\n</body>')
    with open(file_path, 'w') as f:
        f.write(html)
    print(f"  🎨 injected theme \u2192 {os.path.relpath(file_path, SITE_DIR)}")


def build_page(src_path, dest_path):
    """Build a single page from markdown source."""
    with open(src_path, "r") as f:
        raw = f.read()
    
    fm, md_content = parse_front_matter(raw)
    html_content = md_to_html(md_content)
    
    # Merge front matter with standard vars
    page_vars = dict(fm)
    
    # Apply layout
    layout = fm.get("layout", "default")
    full_html = resolve_layout(layout, page_vars, html_content)
    
    # Write output
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(full_html)
    
    print(f"  ✓ {src_path} → {dest_path}")

def build():
    """Build entire site."""
    os.makedirs(BUILD_DIR, exist_ok=True)
    
    print("Building site...")
    
    # Build root pages
    pages = [
        ("index.md", "index.html"),
        ("about.md", "about/index.html"),
    ]
    
    for src, dest in pages:
        src_full = os.path.join(SITE_DIR, src)
        dest_full = os.path.join(BUILD_DIR, dest)
        if os.path.exists(src_full):
            build_page(src_full, dest_full)
    

    
    SKIP_DIRS = {"_site", "_layouts", "_includes", "_posts", ".git"}
    SKIP_PREFIXES = (".", "_")
    SKIP_EXTENSIONS = (".md", ".markdown")
    
    for root, dirs, files in os.walk(SITE_DIR, topdown=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(SKIP_PREFIXES)]
        for f in files:
            if f.startswith(SKIP_PREFIXES) or f.endswith(SKIP_EXTENSIONS):
                continue
            src = os.path.join(root, f)
            rel = os.path.relpath(src, SITE_DIR)
            if rel.startswith(SKIP_PREFIXES):
                continue
            dest = os.path.join(BUILD_DIR, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
            if f.endswith(".html") and rel.startswith("docs"):
                inject_docs_theme(dest)
            else:
                print(f"  → {rel}")
    
    # Copy _site to serve root for simplicity
    print(f"\nSite built at: {BUILD_DIR}")

if __name__ == "__main__":
    build()
