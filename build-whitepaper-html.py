#!/usr/bin/env python3
"""Build house-format whitepaper HTML from whitepaper.md.

House style SSoT: docs/gtm/whitepaper-house-style.md (vault) + this script.
Always write BOTH index.html and docs/harness-first-agentic-ai/index.html.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD = ROOT / "whitepaper.md"
OUTS = [
    ROOT / "index.html",
    ROOT / "docs" / "harness-first-agentic-ai" / "index.html",
]

STYLE = r"""
@page {
    size: letter;
    margin: 1in 1.2in;
}
body {
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #1a1a1a;
    max-width: 6.5in;
    margin: 0 auto;
    padding: 0.5in 0;
}
h1 {
    font-size: 22pt;
    font-weight: 700;
    color: #0d1b2a;
    margin-bottom: 0.3in;
    padding-bottom: 0.15in;
    border-bottom: 2px solid #0d1b2a;
    page-break-after: avoid;
}
h2 {
    font-size: 15pt;
    font-weight: 700;
    color: #0d1b2a;
    margin-top: 0.4in;
    margin-bottom: 0.15in;
    padding-top: 0.1in;
    border-top: 1px solid #ccc;
    page-break-after: avoid;
}
h3 {
    font-size: 12pt;
    font-weight: 600;
    color: #333;
    margin-top: 0.3in;
    margin-bottom: 0.1in;
    page-break-after: avoid;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.25in 0;
    font-size: 10pt;
    page-break-inside: avoid;
}
th {
    background: #0d1b2a;
    color: white;
    padding: 6px 10px;
    text-align: left;
    font-weight: 600;
}
td {
    padding: 5px 10px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}
tr:nth-child(even) {
    background: #f8f9fa;
}
strong {
    color: #0d1b2a;
}
hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 0.3in 0;
}
a {
    color: #1a5276;
    text-decoration: none;
}
a[href^="#"] {
    color: inherit;
    text-decoration: underline;
}
ol, ul {
    padding-left: 0.35in;
}
li {
    margin-bottom: 0.12in;
}
p {
    margin: 0.2in 0;
    text-align: justify;
}
blockquote {
    border-left: 3px solid #0d1b2a;
    padding-left: 0.3in;
    margin: 0.25in 0;
    color: #444;
    font-style: italic;
}
#toc {
    page-break-after: always;
}
#toc h2 {
    border-top: none;
    font-size: 16pt;
}
#toc > ol {
    list-style: none;
    padding-left: 0.5in;
    counter-reset: toc-counter;
}
#toc > ol > li {
    counter-increment: toc-counter;
    margin-bottom: 0.15in;
}
#toc > ol > li::before {
    content: counter(toc-counter) ". ";
    font-weight: 600;
    color: #0d1b2a;
}
#toc a {
    color: inherit;
}
#toc ul {
    list-style: none;
    padding-left: 0.35in;
    margin-top: 0.08in;
}
#toc ul > li {
    margin-bottom: 0.08in;
    font-size: 10pt;
    color: #333;
}
#content h2:first-of-type {
    border-top: none;
}
"""


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s.strip("-")


def inline(md: str) -> str:
    # escape first then restore formatting
    # process in order: code, bold, links, italics
    parts = []
    i = 0
    # simple sequential
    text = md
    # links [t](#a) or [t](url)
    def link_sub(m):
        return f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'

    # temporary protect code
    codes = []

    def save_code(m):
        codes.append(m.group(1))
        return f"\x00C{len(codes)-1}\x00"

    text = re.sub(r"`([^`]+)`", save_code, text)
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    for idx, c in enumerate(codes):
        text = text.replace(f"\x00C{idx}\x00", f"<code>{html.escape(c)}</code>")
    return text


def parse_table(lines: list[str], start: int) -> tuple[str, int]:
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        rows.append(row)
        i += 1
    if len(rows) < 2:
        return "", start
    # skip separator
    body_rows = rows[2:] if re.match(r"^[\s\-:|]+$", "".join(rows[1])) else rows[1:]
    header = rows[0]
    out = ["<table>", "<thead><tr>"]
    for h in header:
        out.append(f"<th>{inline(h)}</th>")
    out.append("</tr></thead><tbody>")
    for r in body_rows:
        out.append("<tr>")
        for j, cell in enumerate(r):
            out.append(f"<td>{inline(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out), i


def md_body_to_html(body: str) -> tuple[str, list[tuple[str, str, list[tuple[str, str]]]]]:
    """Return (html, toc_structure) toc = [(num, title, [(subnum, subtitle)])]"""
    lines = body.splitlines()
    out: list[str] = []
    toc: list[tuple[str, str, list[tuple[str, str]]]] = []
    i = 0
    para: list[str] = []
    in_bq = False
    list_type = None  # ul/ol
    list_items: list[str] = []

    def flush_para():
        nonlocal para
        if para:
            text = " ".join(para).strip()
            if text:
                out.append(f"<p>{inline(text)}</p>")
            para = []

    def flush_list():
        nonlocal list_type, list_items
        if list_type and list_items:
            out.append(f"<{list_type}>")
            for it in list_items:
                out.append(f"<li>{inline(it)}</li>")
            out.append(f"</{list_type}>")
        list_type = None
        list_items = []

    while i < len(lines):
        line = lines[i]
        raw = line
        s = line.strip()

        if not s:
            flush_para()
            flush_list()
            if in_bq:
                out.append("</blockquote>")
                in_bq = False
            i += 1
            continue

        # skip TOC section in body (we build house TOC separately)
        if s == "## Table of Contents" or s.startswith("## Table of Contents"):
            flush_para()
            flush_list()
            i += 1
            while i < len(lines) and not (
                lines[i].startswith("## ") and "Table of Contents" not in lines[i]
            ):
                # stop at --- after toc or next real ##
                if lines[i].strip() == "---" and i + 1 < len(lines):
                    # peek if next non-empty is ## 1.
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and lines[j].startswith("## "):
                        i += 1
                        break
                i += 1
            continue

        if s == "---":
            flush_para()
            flush_list()
            out.append("<hr />")
            i += 1
            continue

        if s.startswith("> "):
            flush_para()
            flush_list()
            if not in_bq:
                out.append("<blockquote>")
                in_bq = True
            out.append(f"<p>{inline(s[2:])}</p>")
            i += 1
            continue
        elif in_bq:
            out.append("</blockquote>")
            in_bq = False

        if s.startswith("|") and "|" in s[1:]:
            flush_para()
            flush_list()
            table_html, i = parse_table(lines, i)
            out.append(table_html)
            continue

        m2 = re.match(r"^## (.+)$", s)
        m3 = re.match(r"^### (.+)$", s)
        if m2:
            flush_para()
            flush_list()
            title = m2.group(1).strip()
            # strip leading number for display id
            sid = slugify(title)
            # extract number if present
            nm = re.match(r"^(\d+)\.\s+(.*)$", title)
            if nm:
                num, rest = nm.group(1), nm.group(2)
                toc.append((num, rest, []))
                out.append(f'<h2 id="{sid}">{html.escape(title)}</h2>')
            else:
                out.append(f'<h2 id="{sid}">{html.escape(title)}</h2>')
            i += 1
            continue
        if m3:
            flush_para()
            flush_list()
            title = m3.group(1).strip()
            sid = slugify(title)
            nm = re.match(r"^(\d+\.\d+)\s+(.*)$", title)
            if nm and toc:
                toc[-1][2].append((nm.group(1), nm.group(2)))
            out.append(f'<h3 id="{sid}">{html.escape(title)}</h3>')
            i += 1
            continue

        # lists
        um = re.match(r"^[-*]\s+(.+)$", s)
        om = re.match(r"^\d+\.\s+(.+)$", s)
        if um or om:
            flush_para()
            kind = "ul" if um else "ol"
            item = um.group(1) if um else om.group(1)
            if list_type and list_type != kind:
                flush_list()
            list_type = kind
            list_items.append(item)
            i += 1
            continue
        else:
            flush_list()

        # paragraph accumulation
        para.append(s)
        i += 1

    flush_para()
    flush_list()
    if in_bq:
        out.append("</blockquote>")
    return "\n".join(out), toc


def build_toc_html(toc: list[tuple[str, str, list[tuple[str, str]]]]) -> str:
    parts = ["<ol>"]
    for num, title, subs in toc:
        sid = slugify(f"{num}. {title}")
        parts.append("<li>")
        parts.append(f'<a href="#{sid}">{html.escape(title)}</a>')
        if subs:
            parts.append("<ul>")
            for sn, st in subs:
                ssid = slugify(f"{sn} {st}")
                parts.append(f'<li><a href="#{ssid}">{html.escape(sn)} {html.escape(st)}</a></li>')
            parts.append("</ul>")
        parts.append("</li>")
    parts.append("</ol>")
    return "\n".join(parts)


def main() -> None:
    raw = MD.read_text(encoding="utf-8")
    lines = raw.splitlines()
    # Title from first H1
    title_line = lines[0].lstrip("# ").strip() if lines else "Whitepaper"
    # Prefer short title + subtitle split on ": "
    if ": " in title_line:
        short, subtitle = title_line.split(": ", 1)
    else:
        short, subtitle = title_line, ""

    # Meta lines after title (bold lines)
    meta = []
    i = 1
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("**") and s.endswith("**"):
            meta.append(s.strip("*").strip())
            i += 1
        elif not s or s == "---":
            i += 1
            if s == "---":
                break
        else:
            break

    # Rest of file from first ## or remaining
    rest = "\n".join(lines[i:])
    body_html, toc = md_body_to_html(rest)
    # If toc empty (filtered TOC section), rebuild from body headings via second pass
    if not toc:
        _, toc = md_body_to_html(rest)

    full_title = title_line
    meta_ps = "\n".join(
        f'<p style="text-align:center; color:#777; font-size:10pt; margin-top:0; margin-bottom:0.15em;">{html.escape(m)}</p>'
        for m in meta
    )

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(full_title)}</title>
<style>
{STYLE}
</style>
</head>
<body>

<div id="toc">
<h1 style="text-align:center; border-bottom: 3px double #0d1b2a;">{html.escape(short)}</h1>
{f'<h2 style="text-align:center; font-size:13pt; color:#555; border:none; margin-top:0;">{html.escape(subtitle)}</h2>' if subtitle else ""}
{meta_ps}
<hr>
<h2>Table of Contents</h2>
{build_toc_html(toc)}
</div>

<div id="content">
{body_html}
</div>

</body>
</html>
"""
    for out in OUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        print(f"wrote {out} ({len(doc)} bytes)")


if __name__ == "__main__":
    main()
