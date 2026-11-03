#!/usr/bin/env python3
"""개드립(dogdrip.net) 붐업 베스트 크롤러 (Playwright 기반)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://www.dogdrip.net"
BEST_URL = f"{BASE}/boomupbest"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@dataclass
class Comment:
    author: str = ""
    text: str = ""
    likes: int = 0


@dataclass
class Post:
    community: str = "dogdrip"
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
        page.wait_for_timeout(2000)

        links = []
        for a in page.query_selector_all("a"):
            h = a.get_attribute("href") or ""
            t = (a.inner_text() or "").strip()
            if not h or not t or len(t) < 3:
                continue
            if h.startswith("/"):
                h = BASE + h
            if "dogdrip.net" not in h:
                continue
            if "/boomupbest" in h or "page=" in h:
                continue
            # post links are /<number>
            import re
            if not re.search(r"/\d{6,}$", h.split("?")[0]):
                continue
            if any(x["url"] == h for x in links):
                continue
            links.append({"url": h, "title": t})
            if len(links) >= 10:
                break

        print(f"[dogdrip] Found {len(links)} candidate posts")

        for item in links[:8]:
            try:
                print(f"  Fetching: {item['title'][:50]}...")
                page.goto(item["url"], wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
                post = Post(url=item["url"], collected_at=datetime.now().isoformat())
                post.title = item["title"]

                # body text from article/content
                body_el = page.query_selector("article, .document, .content, .xe_content")
                if body_el:
                    post.body = body_el.inner_text().strip()[:1000]
                # images
                for im in page.query_selector_all("img"):
                    src = im.get_attribute("src") or ""
                    if src.startswith("http") and "dogdrip" not in src:
                        if src not in post.images:
                            post.images.append(src)
                post.images = post.images[:5]

                # comments: collect text from comment elements
                seen = set()
                for e in page.query_selector_all('[class*="comment"], li'):
                    t = (e.inner_text() or "").strip()
                    if not t or len(t) < 5 or t in seen:
                        continue
                    # skip if it's the whole page
                    if len(t) > 500:
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
    path = output_dir / f"dogdrip_{timestamp}.json"
    data = [{"community": p.community, "title": p.title, "url": p.url, "body": p.body,
             "images": p.images, "comments": [{"author": c.author, "text": c.text, "likes": c.likes} for c in p.comments],
             "views": p.views, "recommends": p.recommends, "collected_at": p.collected_at} for p in posts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[dogdrip] Saved {len(posts)} posts to {path}")
    return path


if __name__ == "__main__":
    posts = collect()
    if posts:
        save(posts)
    else:
        print("[dogdrip] No posts collected")
