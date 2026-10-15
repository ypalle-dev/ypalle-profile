#!/usr/bin/env python3
"""Build the writing pages from Markdown files in posts/.

Add a note by creating posts/YYYY-MM-DD-slug.md with this front matter:

    ---
    title: Title
    date: YYYY-MM-DD
    description: One sentence for the index and the link preview.
    tags: Dynamics 365, Dataverse
    slug: url-slug
    ---

Then, from this folder, run: python3 build_writing.py
"""

from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
WORDS_PER_MINUTE = 220

PAGE_START = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="author" content="Yeswanth Palle" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta property="og:title" content="{og_title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="{og_type}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="bg-grid" aria-hidden="true"></div>
  <div class="bg-glow bg-glow--a" aria-hidden="true"></div>
  <div class="bg-glow bg-glow--b" aria-hidden="true"></div>
  <header class="topbar">
    <a class="brand" href="../index.html">YP</a>
    <nav class="nav" aria-label="Primary">
      <a href="../index.html">Profile</a>
      <a href="index.html">Writing</a>
      <a href="../index.html#contact">Contact</a>
    </nav>
    <a class="btn btn--ghost topbar__cta" href="../index.html#contact">Get in touch</a>
  </header>
  <main>
"""

PAGE_END = """  </main>
  <footer class="footer">
    <p>© <span id="year"></span> Yeswanth Palle · Field notes on Dynamics 365 and Power Platform</p>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def safe_href(url: str) -> str:
    candidate = url.strip()
    lowered = candidate.lower()
    if lowered.startswith(("javascript:", "data:")):
        return "#"
    if re.match(r"^(https?:|mailto:|/|#|\.{1,2}/|[A-Za-z0-9])", candidate):
        return escape(candidate)
    return "#"


def inline(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    rendered: list[str] = []
    for part in parts:
        if len(part) >= 2 and part.startswith("`") and part.endswith("`"):
            rendered.append(f"<code>{escape(part[1:-1])}</code>")
            continue
        piece = escape(part)
        piece = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", piece)
        piece = re.sub(r"(?<!\*)\*(.+?)\*(?!\*)", r"<em>\1</em>", piece)
        piece = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda match: f'<a href="{safe_href(html.unescape(match.group(2)))}">{match.group(1)}</a>',
            piece,
        )
        rendered.append(piece)
    return "".join(rendered)


def is_block(line: str) -> bool:
    return bool(
        line.startswith(("## ", "### ", "> ", "- ", "```"))
        or line.strip() == "---"
        or re.match(r"\d+\. ", line)
    )


def render_markdown(text: str) -> str:
    lines = text.splitlines()
    blocks: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            language = line[3:].strip()
            index += 1
            code: list[str] = []
            while index < len(lines) and not lines[index].startswith("```"):
                code.append(lines[index])
                index += 1
            class_attr = f' class="language-{escape(language)}"' if language else ""
            blocks.append(f"<pre><code{class_attr}>{escape(chr(10).join(code))}</code></pre>")
        elif line.startswith("### "):
            blocks.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            blocks.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("> "):
            quote = [line[2:]]
            while index + 1 < len(lines) and lines[index + 1].startswith("> "):
                index += 1
                quote.append(lines[index][2:])
            blocks.append(f"<blockquote><p>{inline(' '.join(quote))}</p></blockquote>")
        elif line.startswith("- "):
            items = [line[2:]]
            while index + 1 < len(lines) and lines[index + 1].startswith("- "):
                index += 1
                items.append(lines[index][2:])
            blocks.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
        elif re.match(r"\d+\. ", line):
            items = [re.sub(r"^\d+\. ", "", line)]
            while index + 1 < len(lines) and re.match(r"\d+\. ", lines[index + 1]):
                index += 1
                items.append(re.sub(r"^\d+\. ", "", lines[index]))
            blocks.append("<ol>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ol>")
        elif line.strip() == "---":
            blocks.append("<hr />")
        elif line.strip():
            paragraph = [line.strip()]
            while index + 1 < len(lines) and lines[index + 1].strip() and not is_block(lines[index + 1]):
                index += 1
                paragraph.append(lines[index].strip())
            blocks.append(f"<p>{inline(' '.join(paragraph))}</p>")
        index += 1
    return "\n".join(blocks)


def parse_post(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise SystemExit(f"{path.name} is missing front matter")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise SystemExit(f"{path.name} has unclosed front matter")
    meta: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if not line.strip():
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    required = ("title", "date", "description", "slug")
    missing = [key for key in required if not meta.get(key)]
    if missing:
        raise SystemExit(f"{path.name} is missing {', '.join(missing)}")
    tags = meta.get("tags", "").strip("[]")
    body = parts[2].strip()
    words = re.findall(r"\w+", body)
    return {
        "title": meta["title"],
        "date": datetime.strptime(meta["date"], "%Y-%m-%d"),
        "description": meta["description"],
        "slug": meta["slug"],
        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
        "body": body,
        "html": render_markdown(body),
        "minutes": max(1, round(len(words) / WORDS_PER_MINUTE)),
    }


def chips(tags: list[str]) -> str:
    return '<div class="chips">' + "".join(f"<span>{escape(tag)}</span>" for tag in tags) + "</div>"


def post_card(post: dict, href: str) -> str:
    date_iso = post["date"].strftime("%Y-%m-%d")
    date_label = post["date"].strftime("%B %-d, %Y")
    minute_label = "1 min read" if post["minutes"] == 1 else f"{post['minutes']} min read"
    return f"""<a class="post-card" href="{escape(href)}">
        <div class="post-card__meta">
          <time datetime="{date_iso}">{date_label}</time>
          <span>{minute_label}</span>
        </div>
        <h2>{escape(post["title"])}</h2>
        <p>{escape(post["description"])}</p>
        {chips(post["tags"])}
      </a>"""


def shell(title: str, description: str, body: str, og_type: str) -> str:
    return (
        PAGE_START.format(
            title=escape(title),
            description=escape(description),
            og_title=escape(title),
            og_type=og_type,
        )
        + body
        + PAGE_END
    )


def write_article(post: dict) -> None:
    date_iso = post["date"].strftime("%Y-%m-%d")
    date_label = post["date"].strftime("%B %-d, %Y")
    minute_label = "1 min read" if post["minutes"] == 1 else f"{post['minutes']} min read"
    body = f"""    <article class="article">
      <header class="article__header">
        <p class="crumb"><a href="../index.html">Profile</a><span aria-hidden="true">/</span><a href="index.html">Writing</a></p>
        <div class="post-card__meta">
          <time datetime="{date_iso}">{date_label}</time>
          <span>{minute_label}</span>
        </div>
        <h1>{escape(post["title"])}</h1>
        <p class="article__lede">{escape(post["description"])}</p>
        {chips(post["tags"])}
      </header>
      <div class="prose">
        {post["html"]}
      </div>
      <p class="article__end writing-more"><a href="index.html">All writing</a></p>
    </article>
"""
    path = ROOT / f"{post['slug']}.html"
    path.write_text(
        shell(
            f"{post['title']} · Yeswanth Palle",
            post["description"],
            body,
            "article",
        ),
        encoding="utf-8",
    )


def write_index(posts: list[dict]) -> None:
    cards = "\n".join(post_card(post, f"{post['slug']}.html") for post in posts)
    empty = '<p class="article__lede">The first note is still in draft.</p>' if not posts else ""
    body = f"""    <header class="page-intro">
      <p class="crumb"><a href="../index.html">Profile</a><span aria-hidden="true">/</span>Writing</p>
      <span class="section__eyebrow">Field notes</span>
      <h1>Writing</h1>
      <p>Notes on Dynamics 365, Dataverse, and the pipelines that feed them. One problem at a time, with the option I turned down and the failure path included.</p>
    </header>
    <section class="section section--follow">
      <div class="post-list">
        {cards or empty}
      </div>
    </section>
"""
    (ROOT / "index.html").write_text(
        shell(
            "Writing · Yeswanth Palle",
            "Field notes by Yeswanth Palle on Dynamics 365, Dataverse, Power Platform, and delivery.",
            body,
            "website",
        ),
        encoding="utf-8",
    )


def main() -> None:
    posts = [parse_post(path) for path in sorted(POSTS.glob("*.md"))]
    posts.sort(key=lambda post: post["date"], reverse=True)
    slugs = [post["slug"] for post in posts]
    if len(slugs) != len(set(slugs)):
        raise SystemExit("Two posts share a slug")
    for stale in ROOT.glob("*.html"):
        if stale.name != "index.html" and stale.stem not in slugs:
            stale.unlink()
    for post in posts:
        write_article(post)
    write_index(posts)
    print(f"Built {len(posts)} note{'s' if len(posts) != 1 else ''} into {ROOT}")


if __name__ == "__main__":
    main()
