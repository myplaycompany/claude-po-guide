#!/usr/bin/env python3
"""
Generates a static HTML site from markdown files.
Output: docs/ directory
"""
import os
import re

# ─── Configuration ────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

NAV_ITEMS = [
    {"label": "홈", "href": "../index.html", "root_href": "index.html", "icon": "🏠"},
    {"label": "커리큘럼 목차", "href": "curriculum/index.html", "root_href": "curriculum/index.html", "icon": "📖"},
    {"label": "1강 — 마인드셋", "href": "curriculum/01_mindset.html", "root_href": "curriculum/01_mindset.html", "icon": "💡"},
    {"label": "2강 — 기초 프롬프팅", "href": "curriculum/02_prompting.html", "root_href": "curriculum/02_prompting.html", "icon": "✏️"},
    {"label": "3강 — Soul Document", "href": "curriculum/03_soul_document.html", "root_href": "curriculum/03_soul_document.html", "icon": "📄"},
    {"label": "4강 — PRD 작성", "href": "curriculum/04_prd_writing.html", "root_href": "curriculum/04_prd_writing.html", "icon": "📝"},
    {"label": "5강 — 컨텍스트 쌓기", "href": "curriculum/05_context.html", "root_href": "curriculum/05_context.html", "icon": "🧩"},
    {"label": "6강 — 반복 업무 자동화", "href": "curriculum/06_commands.html", "root_href": "curriculum/06_commands.html", "icon": "⚡"},
    {"label": "7강 — Agentic Workflow", "href": "curriculum/07_agentic.html", "root_href": "curriculum/07_agentic.html", "icon": "🤖"},
    {"label": "8강 — Workflow 완성", "href": "curriculum/08_workflow.html", "root_href": "curriculum/08_workflow.html", "icon": "🏆"},
    {"label": "부록 — 프롬프트 모음", "href": "curriculum/appendix_prompts.html", "root_href": "curriculum/appendix_prompts.html", "icon": "📋"},
    {"label": "─── 템플릿", "href": None, "root_href": None, "icon": ""},
    {"label": "CLAUDE.md 템플릿", "href": "curriculum/templates/CLAUDE_md_template.html", "root_href": "curriculum/templates/CLAUDE_md_template.html", "icon": "🗂️"},
    {"label": "PRD 템플릿", "href": "curriculum/templates/PRD_template.html", "root_href": "curriculum/templates/PRD_template.html", "icon": "📃"},
    {"label": "PROGRESS.md 템플릿", "href": "curriculum/templates/PROGRESS_md_template.html", "root_href": "curriculum/templates/PROGRESS_md_template.html", "icon": "📊"},
]

FILES = [
    # (input_md_path, output_html_path, page_title)
    ("README.md", "index.html", "초보 PO를 위한 Claude 활용 커리큘럼"),
    ("curriculum/PO_Claude_Curriculum.md", "curriculum/index.html", "커리큘럼 목차"),
    ("curriculum/01_mindset.md", "curriculum/01_mindset.html", "1강: 마인드셋 전환"),
    ("curriculum/02_prompting.md", "curriculum/02_prompting.html", "2강: 기초 프롬프팅"),
    ("curriculum/03_soul_document.md", "curriculum/03_soul_document.html", "3강: Soul Document"),
    ("curriculum/04_prd_writing.md", "curriculum/04_prd_writing.html", "4강: PRD 작성"),
    ("curriculum/05_context.md", "curriculum/05_context.html", "5강: 컨텍스트 쌓기"),
    ("curriculum/06_commands.md", "curriculum/06_commands.html", "6강: 반복 업무 자동화"),
    ("curriculum/07_agentic.md", "curriculum/07_agentic.html", "7강: Agentic Workflow"),
    ("curriculum/08_workflow.md", "curriculum/08_workflow.html", "8강: Workflow 완성"),
    ("curriculum/appendix_prompts.md", "curriculum/appendix_prompts.html", "부록: 프롬프트 모음"),
    ("curriculum/templates/CLAUDE_md_template.md", "curriculum/templates/CLAUDE_md_template.html", "CLAUDE.md 템플릿"),
    ("curriculum/templates/PRD_template.md", "curriculum/templates/PRD_template.html", "PRD 템플릿"),
    ("curriculum/templates/PROGRESS_md_template.md", "curriculum/templates/PROGRESS_md_template.html", "PROGRESS.md 템플릿"),
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def fix_md_links(content):
    """Convert .md links to .html links (skip external URLs).
    README.md → index.html
    """
    def replace(m):
        text, url = m.group(1), m.group(2)
        if url.startswith("http"):
            return m.group(0)
        if url.endswith(".md"):
            base = url[:-3]
            # README → index
            if base == "README" or base.endswith("/README"):
                base = base[:-6] + "index" if base.endswith("/README") else "index"
            url = base + ".html"
        return f"[{text}]({url})"
    return re.sub(r'\[([^\]]*)\]\(([^)]+)\)', replace, content)


def escape_js_template(content):
    """Escape content for embedding inside a JS template literal."""
    content = content.replace("\\", "\\\\")
    content = content.replace("`", "\\`")
    content = content.replace("${", "\\${")
    return content


def build_nav_html(current_output_path):
    """Build sidebar navigation HTML with correct relative paths."""
    current_dir = os.path.dirname(current_output_path)
    items_html = []
    for item in NAV_ITEMS:
        target = item["root_href"]
        icon = item["icon"]
        label = item["label"]

        if target is None:
            items_html.append(f'<li class="nav-section">{label}</li>')
            continue

        # Compute relative path from current page's directory to target
        rel = os.path.relpath(target, current_dir) if current_dir else target
        # os.path.relpath uses OS separator; normalize to /
        rel = rel.replace("\\", "/")

        is_active = (current_output_path == target)
        active_class = " active" if is_active else ""
        items_html.append(
            f'<li><a href="{rel}" class="nav-link{active_class}">'
            f'<span class="nav-icon">{icon}</span>{label}</a></li>'
        )
    return "\n".join(items_html)


def generate_html(md_content, title, output_path):
    """Wrap markdown content in a full HTML page."""
    nav_html = build_nav_html(output_path)
    escaped_md = escape_js_template(fix_md_links(md_content))
    cur_dir = os.path.dirname(output_path)
    home_href = os.path.relpath("index.html", cur_dir).replace("\\", "/") if cur_dir else "index.html"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — AI PO Study</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css" />
  <style>
    /* ── Reset & Base ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --sidebar-w: 260px;
      --color-bg: #f8f9fb;
      --color-surface: #ffffff;
      --color-border: #e5e7eb;
      --color-primary: #4f46e5;
      --color-primary-light: #eef2ff;
      --color-text: #1f2937;
      --color-muted: #6b7280;
      --color-code-bg: #f3f4f6;
      --radius: 8px;
      --shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.05);
    }}
    html {{ font-size: 16px; scroll-behavior: smooth; }}
    body {{
      font-family: 'Noto Sans KR', -apple-system, sans-serif;
      background: var(--color-bg);
      color: var(--color-text);
      line-height: 1.7;
      display: flex;
      min-height: 100vh;
    }}

    /* ── Sidebar ── */
    .sidebar {{
      position: fixed;
      top: 0; left: 0; bottom: 0;
      width: var(--sidebar-w);
      background: var(--color-surface);
      border-right: 1px solid var(--color-border);
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      z-index: 100;
    }}
    .sidebar-brand {{
      padding: 20px 20px 16px;
      border-bottom: 1px solid var(--color-border);
    }}
    .sidebar-brand a {{
      text-decoration: none;
      color: var(--color-primary);
      font-weight: 700;
      font-size: .9rem;
      line-height: 1.4;
    }}
    .sidebar-brand span {{
      display: block;
      font-size: .72rem;
      color: var(--color-muted);
      font-weight: 400;
      margin-top: 2px;
    }}
    .sidebar nav {{ padding: 12px 0 24px; }}
    .sidebar nav ul {{ list-style: none; }}
    .nav-section {{
      padding: 16px 20px 4px;
      font-size: .7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: .07em;
      color: var(--color-muted);
    }}
    .nav-link {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 7px 20px;
      font-size: .83rem;
      color: var(--color-text);
      text-decoration: none;
      border-radius: 0;
      transition: background .15s, color .15s;
      border-left: 3px solid transparent;
    }}
    .nav-link:hover {{ background: var(--color-primary-light); color: var(--color-primary); }}
    .nav-link.active {{
      background: var(--color-primary-light);
      color: var(--color-primary);
      border-left-color: var(--color-primary);
      font-weight: 600;
    }}
    .nav-icon {{ font-size: .9rem; flex-shrink: 0; width: 20px; text-align: center; }}

    /* ── Main ── */
    .main {{
      margin-left: var(--sidebar-w);
      flex: 1;
      min-width: 0;
      padding: 40px 48px;
      max-width: calc(860px + var(--sidebar-w));
    }}

    /* ── Markdown Content ── */
    .prose {{ max-width: 760px; }}
    .prose h1 {{
      font-size: 2rem;
      font-weight: 700;
      line-height: 1.25;
      margin-bottom: 8px;
      color: var(--color-text);
    }}
    .prose h2 {{
      font-size: 1.35rem;
      font-weight: 700;
      margin-top: 40px;
      margin-bottom: 14px;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--color-border);
      color: var(--color-text);
    }}
    .prose h3 {{
      font-size: 1.1rem;
      font-weight: 600;
      margin-top: 28px;
      margin-bottom: 10px;
      color: var(--color-text);
    }}
    .prose h4 {{
      font-size: 1rem;
      font-weight: 600;
      margin-top: 20px;
      margin-bottom: 8px;
      color: #374151;
    }}
    .prose p {{ margin-bottom: 14px; }}
    .prose ul, .prose ol {{
      margin-bottom: 14px;
      padding-left: 24px;
    }}
    .prose li {{ margin-bottom: 5px; }}
    .prose li > ul, .prose li > ol {{ margin-top: 5px; margin-bottom: 5px; }}

    .prose strong {{ font-weight: 600; }}
    .prose em {{ font-style: italic; }}

    .prose a {{
      color: var(--color-primary);
      text-decoration: none;
      border-bottom: 1px solid rgba(79,70,229,.3);
      transition: border-color .15s;
    }}
    .prose a:hover {{ border-bottom-color: var(--color-primary); }}

    .prose blockquote {{
      margin: 20px 0;
      padding: 12px 18px;
      background: var(--color-primary-light);
      border-left: 4px solid var(--color-primary);
      border-radius: 0 var(--radius) var(--radius) 0;
      color: #3730a3;
    }}
    .prose blockquote p {{ margin-bottom: 0; }}

    .prose hr {{
      border: none;
      border-top: 1px solid var(--color-border);
      margin: 32px 0;
    }}

    /* Tables */
    .prose table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
      font-size: .88rem;
      box-shadow: var(--shadow);
      border-radius: var(--radius);
      overflow: hidden;
    }}
    .prose thead tr {{ background: var(--color-primary); color: #fff; }}
    .prose th {{
      padding: 10px 14px;
      text-align: left;
      font-weight: 600;
    }}
    .prose td {{
      padding: 9px 14px;
      border-bottom: 1px solid var(--color-border);
    }}
    .prose tbody tr:last-child td {{ border-bottom: none; }}
    .prose tbody tr:hover {{ background: var(--color-primary-light); }}

    /* Code */
    .prose code {{
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: .82em;
      background: var(--color-code-bg);
      padding: 2px 6px;
      border-radius: 4px;
      color: #b91c1c;
    }}
    .prose pre {{
      margin: 18px 0;
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow);
    }}
    .prose pre code {{
      background: none;
      padding: 0;
      color: inherit;
      font-size: .83rem;
      line-height: 1.6;
    }}
    .prose pre > code.hljs {{ padding: 20px 24px; border-radius: var(--radius); }}

    /* Checkboxes in lists */
    .prose input[type="checkbox"] {{
      margin-right: 6px;
      accent-color: var(--color-primary);
    }}

    /* ── Mobile ── */
    .menu-btn {{
      display: none;
      position: fixed;
      top: 14px; left: 14px;
      z-index: 200;
      background: var(--color-primary);
      color: #fff;
      border: none;
      border-radius: 8px;
      width: 40px; height: 40px;
      font-size: 1.2rem;
      cursor: pointer;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 8px rgba(79,70,229,.4);
    }}
    .sidebar-overlay {{
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,.4);
      z-index: 99;
    }}
    @media (max-width: 768px) {{
      .menu-btn {{ display: flex; }}
      .sidebar {{ transform: translateX(-100%); transition: transform .25s; }}
      .sidebar.open {{ transform: none; }}
      .sidebar-overlay.open {{ display: block; }}
      .main {{ margin-left: 0; padding: 20px 18px 40px; }}
    }}
  </style>
</head>
<body>

<button class="menu-btn" id="menuBtn" aria-label="메뉴 열기">☰</button>
<div class="sidebar-overlay" id="overlay"></div>

<aside class="sidebar" id="sidebar">
  <div class="sidebar-brand">
    <a href="{home_href}">📚 AI PO Study<span>초보 PO를 위한 Claude 활용 커리큘럼</span></a>
  </div>
  <nav>
    <ul>
      {nav_html}
    </ul>
  </nav>
</aside>

<main class="main">
  <article class="prose" id="content"></article>
</main>

<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script>
  // Configure marked
  marked.setOptions({{
    breaks: true,
    gfm: true,
    highlight: function(code, lang) {{
      if (lang && hljs.getLanguage(lang)) {{
        return hljs.highlight(code, {{ language: lang }}).value;
      }}
      return hljs.highlightAuto(code).value;
    }}
  }});

  const md = `{escaped_md}`;
  document.getElementById('content').innerHTML = marked.parse(md);

  // Syntax highlight all code blocks
  document.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));

  // Mobile menu
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('overlay');
  const menuBtn  = document.getElementById('menuBtn');
  menuBtn.addEventListener('click', () => {{
    sidebar.classList.toggle('open');
    overlay.classList.toggle('open');
  }});
  overlay.addEventListener('click', () => {{
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
  }});
</script>
</body>
</html>"""


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "curriculum"), exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "curriculum", "templates"), exist_ok=True)

    for md_rel, html_rel, title in FILES:
        md_path   = os.path.join(BASE_DIR, md_rel)
        html_path = os.path.join(DOCS_DIR, html_rel)

        with open(md_path, encoding="utf-8") as f:
            md_content = f.read()

        html = generate_html(md_content, title, html_rel)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  ✓  {html_rel}")

    print(f"\nDone! Open docs/index.html in your browser.")


if __name__ == "__main__":
    main()
