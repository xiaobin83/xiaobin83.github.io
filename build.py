#!/usr/bin/env python3
"""Minimal Jekyll-style static site builder for this project."""

import re
import os
import yaml
from datetime import datetime

SITE_DIR = "/home/xiaobin/Workspace/xiaobin83.github.io"
BUILD_DIR = os.path.join(SITE_DIR, "_site")
SITE_CONFIG = {
    "title": "0x600d1dea",
    "email": "xiaobin.huang@gmail.com",
    "description": "Write an awesome description for your new site here.",
    "baseurl": "",
    "url": "",
    "twitter_username": "xiaobin_huang",
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
    

    
    import shutil
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
            print(f"  → {rel}")
    
    # Copy _site to serve root for simplicity
    print(f"\nSite built at: {BUILD_DIR}")

if __name__ == "__main__":
    build()
