#!/usr/bin/env python3
"""엠팍(mlbpark.donga.com) 유머 게시판 크롤러 (Playwright 기반)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://mlbpark.donga.com"
BEST_URL = f"{BASE}/mp/b.php"  # main list (recent)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@dataclass
class Comment:
    author: str = ""
    text: str = ""
    likes: int = 0


@dataclass
class Post:
    community: str = "mlbpark"
    title: str = ""
    url: str = ""
    body: str = ""
    images: list[str] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    views: int = 0
    recommends: int = 0
    collected_at: str = ""


def collect() -> list[Post]:
    posts = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
        page.goto(BEST_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        links = []
        for a in page.query_selector_all("a"):
            h = a.get_attribute("href") or ""
            t = (a.inner_text() or "").strip()
            if not h or not t or len(t) < 4:
                continue
            if h.startswith("/"):
                h = "https://mlbpark.donga.com" + h
            if "mlbpark.donga.com" not in h:
                continue
            if any(x["url"] == h for x in links):
                continue
            if "mlbpark.donga.com" not in h:
                continue
            if "id=" not in h:
                continue
            if "notice" in h or "b=notice" in h:
                continue
            if any(k in t for k in ["공지", "말머리", "업데이트", "🛠", "🚨", "⚾", "필독"]):
                continue
            links.append({"url": h, "title": t})
            if len(links) >= 12:
                break

        # keep only view links
        filtered = [l for l in links if "id=" in l["url"] or "view" in l["url"]]
        if filtered:
            links = filtered[:8]

        print(f"[mlbpark] Found {len(links)} candidate posts")

        for item in links:
            try:
                print(f"  Fetching: {item['title'][:50]}...")
                page.goto(item["url"], wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(1500)
                post = Post(url=item["url"], collected_at=datetime.now().isoformat())
                post.title = item["title"]

                for sel in ["h1", "h2", "h3", ".title", "title"]:
                    el = page.query_selector(sel)
                    if el:
                        tt = el.inner_text().strip()
                        if tt and len(tt) > 3 and "mlbpark" not in tt.lower():
                            post.title = tt
                            break

                body_el = page.query_selector("article, .content, .view_content, #content, td")
                if body_el:
                    post.body = body_el.inner_text().strip()[:1000]

                for im in page.query_selector_all("img"):
                    src = im.get_attribute("src") or ""
                    if src.startswith("//"):
                        src = "https:" + src
                    if src.startswith("http") and "mlbpark" not in src and "donga" not in src:
                        if src not in post.images:
                            post.images.append(src)
                post.images = post.images[:5]

                seen = set()
                for e in page.query_selector_all('[class*="comment"], li, p, td'):
                    t = (e.inner_text() or "").strip()
                    if not t or len(t) < 5 or t in seen or len(t) > 400:
                        continue
                    seen.add(t)
                    post.comments.append(Comment(text=t[:200]))
                post.comments = post.comments[:20]

                posts.append(post)
                print(f"    Body: {len(post.body)} chars, Images: {len(post.images)}, Comments: {len(post.comments)}")
            except Exception as e:
                print(f"  Error: {e}")

        browser.close()
    return posts


def save(posts, output_dir=OUTPUT_DIR):
    import json
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"mlbpark_{timestamp}.json"
    data = [{"community": p.community, "title": p.title, "url": p.url, "body": p.body,
             "images": p.images, "comments": [{"author": c.author, "text": c.text, "likes": c.likes} for c in p.comments],
             "views": p.views, "recommends": p.recommends, "collected_at": p.collected_at} for p in posts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[mlbpark] Saved {len(posts)} posts to {path}")
    return path


if __name__ == "__main__":
    posts = collect()
    if posts:
        save(posts)
    else:
        print("[mlbpark] No posts collected")
