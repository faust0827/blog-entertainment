#!/usr/bin/env python3
"""FM코리아(fmkorea.com) 포텐터짐 베스트 크롤러 (Playwright 기반)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://www.fmkorea.com"
BEST_URL = f"{BASE}/best"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@dataclass
class Comment:
    author: str = ""
    text: str = ""
    likes: int = 0


@dataclass
class Post:
    community: str = "fmkorea"
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
                h = BASE + h
            if "fmkorea.com" not in h:
                continue
            if "/best" in h and ("page=" in h or "cpage=" in h):
                continue
            # post links contain document_srl or numeric path
            if not (re.search(r"/\d{6,}", h) or "document_srl=" in h or "mid=best" in h and "document" in h):
                # fmkorea post urls usually /{number} or /index.php?...&document_srl=
                if "/best" in h:
                    continue
            if any(x["url"] == h for x in links):
                continue
            # skip navigation/category links
            if t.endswith("]"):
                pass
            links.append({"url": h, "title": t})
            if len(links) >= 12:
                break

        # filter to likely post links: contain a number and not category
        filtered = []
        for l in links:
            if re.search(r"/\d{7,}", l["url"]) or "document_srl=" in l["url"]:
                filtered.append(l)
        if filtered:
            links = filtered[:8]

        print(f"[fmkorea] Found {len(links)} candidate posts")

        for item in links[:8]:
            try:
                print(f"  Fetching: {item['title'][:50]}...")
                page.goto(item["url"], wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)
                post = Post(url=item["url"], collected_at=datetime.now().isoformat())
                post.title = item["title"]

                # title from h1/h2
                for sel in ["h1", "h2", ".title", ".np_18px_span"]:
                    el = page.query_selector(sel)
                    if el:
                        tt = el.inner_text().strip()
                        if tt and len(tt) > 3:
                            post.title = tt
                            break

                # body
                body_el = page.query_selector("#bd_capture .xe_content, #bd_capture, .xe_content, article")
                if body_el:
                    post.body = body_el.inner_text().strip()[:1000]

                # images
                for im in page.query_selector_all("img"):
                    src = im.get_attribute("src") or ""
                    if src.startswith("//"):
                        src = "https:" + src
                    if src.startswith("http") and "fmkorea" not in src and "icon" not in src:
                        if src not in post.images:
                            post.images.append(src)
                post.images = post.images[:5]

                # comments
                seen = set()
                for e in page.query_selector_all('[class*="comment"], li'):
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
    path = output_dir / f"fmkorea_{timestamp}.json"
    data = [{"community": p.community, "title": p.title, "url": p.url, "body": p.body,
             "images": p.images, "comments": [{"author": c.author, "text": c.text, "likes": c.likes} for c in p.comments],
             "views": p.views, "recommends": p.recommends, "collected_at": p.collected_at} for p in posts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[fmkorea] Saved {len(posts)} posts to {path}")
    return path


if __name__ == "__main__":
    posts = collect()
    if posts:
        save(posts)
    else:
        print("[fmkorea] No posts collected")
