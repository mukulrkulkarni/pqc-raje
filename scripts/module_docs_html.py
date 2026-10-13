#!/usr/bin/env python3
"""Generate HTML documentation from markdown and source files.

Creates two outputs:
1. Standalone HTML from markdown
2. Side-by-side view with code (line numbers) and documentation
"""

import argparse
import html
import re
import sys
from pathlib import Path

# Hardened CSP - no external resources
CSP = (
    "default-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "frame-ancestors 'none'; "
    "connect-src 'none'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "script-src 'unsafe-inline'; "
    "style-src 'unsafe-inline';"
)

# Design tokens
CSS_TOKENS = """
:root {
  --color-bg: #ffffff;
  --color-bg-alt: #f8f9fa;
  --color-text: #1a1a2e;
  --color-text-muted: #6c757d;
  --color-primary: #2563eb;
  --color-border: #e5e7eb;
  --color-code-bg: #f1f5f9;
  --font-sans: Arial, sans-serif;
  --font-mono: 'Consolas', 'Monaco', monospace;
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --radius-sm: 4px;
  --radius-md: 8px;
}
"""

CSS_BASE = CSS_TOKENS + """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font-sans);
  font-size: 16px;
  line-height: 1.6;
  color: var(--color-text);
  background: var(--color-bg);
  padding: var(--space-xl);
  max-width: 900px;
  margin: 0 auto;
}
h1 { font-size: 2rem; margin-bottom: var(--space-lg); border-bottom: 2px solid var(--color-primary); padding-bottom: var(--space-sm); }
h2 { font-size: 1.5rem; margin-top: var(--space-xl); margin-bottom: var(--space-md); color: var(--color-primary); }
h3 { font-size: 1.25rem; margin-top: var(--space-lg); margin-bottom: var(--space-sm); }
p { margin-bottom: var(--space-md); }
code {
  font-family: var(--font-mono);
  font-size: 0.9em;
  background: var(--color-code-bg);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
}
pre {
  background: var(--color-code-bg);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin-bottom: var(--space-md);
}
pre code { background: none; padding: 0; }
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--space-md);
}
th, td {
  border: 1px solid var(--color-border);
  padding: var(--space-sm) var(--space-md);
  text-align: left;
}
th { background: var(--color-bg-alt); font-weight: 600; }
ul, ol { margin-bottom: var(--space-md); padding-left: var(--space-xl); }
li { margin-bottom: var(--space-xs); }
strong { font-weight: 600; }
"""

CSS_SIDE = CSS_TOKENS + """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-bg);
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.header {
  background: var(--color-primary);
  color: white;
  padding: var(--space-sm) var(--space-md);
  font-weight: 600;
  flex-shrink: 0;
}
.container {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.pane {
  flex: 1;
  overflow: auto;
  padding: var(--space-md);
}
.pane-code {
  background: var(--color-code-bg);
  border-right: 1px solid var(--color-border);
  font-family: var(--font-mono);
  font-size: 13px;
  white-space: pre;
}
.pane-doc { background: var(--color-bg); }
.pane-header {
  font-weight: 600;
  padding: var(--space-sm) var(--space-md);
  background: var(--color-bg-alt);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
}
.line-num {
  display: inline-block;
  width: 3em;
  color: var(--color-text-muted);
  text-align: right;
  padding-right: var(--space-sm);
  user-select: none;
}
h1 { font-size: 1.5rem; margin-bottom: var(--space-md); }
h2 { font-size: 1.25rem; margin-top: var(--space-lg); margin-bottom: var(--space-sm); color: var(--color-primary); }
h3 { font-size: 1.1rem; margin-top: var(--space-md); margin-bottom: var(--space-xs); }
p { margin-bottom: var(--space-sm); }
code { font-family: var(--font-mono); font-size: 0.9em; background: var(--color-code-bg); padding: 2px 4px; border-radius: 3px; }
pre { background: var(--color-code-bg); padding: var(--space-sm); border-radius: var(--radius-sm); overflow-x: auto; margin-bottom: var(--space-sm); }
pre code { background: none; padding: 0; }
table { width: 100%; border-collapse: collapse; margin-bottom: var(--space-sm); font-size: 0.9em; }
th, td { border: 1px solid var(--color-border); padding: var(--space-xs) var(--space-sm); text-align: left; }
th { background: var(--color-bg-alt); }
ul, ol { margin-bottom: var(--space-sm); padding-left: var(--space-lg); }
@media (max-width: 900px) {
  .container { flex-direction: column; }
  .pane-code { border-right: none; border-bottom: 1px solid var(--color-border); max-height: 40vh; }
}
"""


def md_to_html(md: str) -> str:
    """Convert markdown to HTML (simple subset)."""
    lines = md.split('\n')
    html_lines = []
    in_code = False
    in_table = False
    in_list = False
    list_type = None

    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code:
                html_lines.append('</code></pre>')
                in_code = False
            else:
                html_lines.append('<pre><code>')
                in_code = True
            continue

        if in_code:
            html_lines.append(html.escape(line))
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(set(c) <= set('-:') for c in cells):
                continue  # Skip separator row
            if not in_table:
                html_lines.append('<table>')
                in_table = True
                tag = 'th'
            else:
                tag = 'td'
            row = ''.join(f'<{tag}>{html.escape(c)}</{tag}>' for c in cells)
            html_lines.append(f'<tr>{row}</tr>')
            continue
        elif in_table:
            html_lines.append('</table>')
            in_table = False

        # Lists
        ul_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
        if ul_match or ol_match:
            match = ul_match or ol_match
            new_type = 'ul' if ul_match else 'ol'
            if not in_list:
                html_lines.append(f'<{new_type}>')
                in_list = True
                list_type = new_type
            content = process_inline(match.group(2))
            html_lines.append(f'<li>{content}</li>')
            continue
        elif in_list and line.strip() == '':
            html_lines.append(f'</{list_type}>')
            in_list = False
            list_type = None

        # Headers
        h_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if h_match:
            level = len(h_match.group(1))
            text = process_inline(h_match.group(2))
            html_lines.append(f'<h{level}>{text}</h{level}>')
            continue

        # Paragraphs
        if line.strip():
            html_lines.append(f'<p>{process_inline(line)}</p>')
        else:
            html_lines.append('')

    # Close any open tags
    if in_code:
        html_lines.append('</code></pre>')
    if in_table:
        html_lines.append('</table>')
    if in_list:
        html_lines.append(f'</{list_type}>')

    return '\n'.join(html_lines)


def process_inline(text: str) -> str:
    """Process inline markdown formatting."""
    text = html.escape(text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def generate_standalone(md_path: Path) -> str:
    """Generate standalone HTML from markdown."""
    md_content = md_path.read_text(encoding='utf-8')
    body = md_to_html(md_content)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{md_path.stem} - ELECTRE III Documentation</title>
<style>{CSS_BASE}</style>
</head>
<body>
{body}
</body>
</html>'''


def generate_side_by_side(md_path: Path, src_path: Path) -> str:
    """Generate side-by-side HTML with code and documentation."""
    md_content = md_path.read_text(encoding='utf-8')
    src_content = src_path.read_text(encoding='utf-8')

    doc_html = md_to_html(md_content)

    # Add line numbers to code
    code_lines = []
    for i, line in enumerate(src_content.split('\n'), 1):
        escaped = html.escape(line) or ' '
        code_lines.append(f'<span class="line-num">{i}</span>{escaped}')
    code_html = '\n'.join(code_lines)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<title>{md_path.stem} - Side by Side</title>
<style>{CSS_SIDE}</style>
</head>
<body>
<div class="header">ELECTRE III Module Documentation: {src_path.name}</div>
<div class="container">
<div class="pane pane-code">
<div class="pane-header">Source Code</div>
<div style="padding: var(--space-md);">{code_html}</div>
</div>
<div class="pane pane-doc">
<div class="pane-header">Documentation</div>
<div style="padding: var(--space-md);">{doc_html}</div>
</div>
</div>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description='Generate HTML module docs')
    parser.add_argument('md_file', type=Path, help='Markdown documentation file')
    parser.add_argument('src_file', type=Path, help='Python source file')
    args = parser.parse_args()

    if not args.md_file.exists():
        print(f"Error: {args.md_file} not found", file=sys.stderr)
        return 1
    if not args.src_file.exists():
        print(f"Error: {args.src_file} not found", file=sys.stderr)
        return 1

    # Generate standalone HTML
    standalone = generate_standalone(args.md_file)
    out_standalone = args.md_file.with_suffix('.html')
    out_standalone.write_text(standalone, encoding='utf-8')
    print(f"Created: {out_standalone}")

    # Generate side-by-side HTML
    side_by_side = generate_side_by_side(args.md_file, args.src_file)
    out_side = args.md_file.with_name(f"{args.md_file.stem}_side_by_side.html")
    out_side.write_text(side_by_side, encoding='utf-8')
    print(f"Created: {out_side}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
