#!/usr/bin/env python3
"""웃긴대학(humoruniv.com) 베스트글 크롤러 (Playwright 기반)."""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://web.humoruniv.com"
BEST_URL = f"{BASE}/board/humor/list.html?table=pds&st=day"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@dataclass
class Comment:
    author: str = ""
    text: str = ""
    likes: int = 0


@dataclass
class Post:
    community: str = "humoruniv"
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

        links = page.evaluate("""() => {
            const anchors = document.querySelectorAll('a[href*="read.html"]');
            const seen = new Set();
            const result = [];
            for (const a of anchors) {
                const href = a.getAttribute('href');
                if (!href || !href.includes('number=')) continue;
                const title = (a.textContent || '').trim();
                if (title.length < 3) continue;
                const fullUrl = href.startsWith('http') ? href : 'https://web.humoruniv.com/board/humor/' + href.replace(/^\\/+/, '');
                if (seen.has(fullUrl)) continue;
                seen.add(fullUrl);
                result.push({url: fullUrl, title: title});
            }
            return result.slice(0, 15);
        }""")

        print(f"[humoruniv] Found {len(links)} candidate posts")

        for item in links[:8]:
            try:
                print(f"  Fetching: {item['title'][:50]}...")
                page.goto(item["url"], wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)

                post = Post(url=item["url"], collected_at=datetime.now().isoformat())

                # Title from og:title or <title>
                title = None
                el = page.query_selector('meta[property="og:title"]')
                if el:
                    title = el.get_attribute("content")
                if not title:
                    te = page.query_selector("title")
                    if te:
                        title = te.inner_text().replace("남을 행복하게 만들어주는, 웃긴대학에 오셨습니다.", "").strip()
                post.title = (title or item["title"]).strip()

                # Body summary from meta description
                desc = None
                el = page.query_selector('meta[name="description"]')
                if el:
                    desc = el.get_attribute("content")
                if not desc:
                    el = page.query_selector('meta[property="og:description"]')
                    if el:
                        desc = el.get_attribute("content")
                post.body = (desc or "").strip()

                # Images (full-size only)
                imgs = page.query_selector_all("img")
                seen_img = set()
                for im in imgs:
                    src = im.get_attribute("src") or ""
                    if "down.humoruniv.com" in src and "timg.humoruniv" not in src:
                        if src not in seen_img:
                            seen_img.add(src)
                            post.images.append(src)
                post.images = post.images[:5]

                # Comments
                seen_c = set()
                for e in page.query_selector_all('[class*="comment"]'):
                    t = (e.inner_text() or "").strip().replace("...전체보기", "").strip()
                    if not t or t.isdigit() or len(t) < 2:
                        continue
                    if t in seen_c:
                        continue
                    seen_c.add(t)
                    post.comments.append(Comment(text=t))
                # keep a reasonable number
                post.comments = post.comments[:20]

                if post.title:
                    posts.append(post)
                    print(f"    Body: {len(post.body)} chars, Images: {len(post.images)}, Comments: {len(post.comments)}")
            except Exception as e:
                print(f"  Error: {e}")

        browser.close()
    return posts


def save(posts: list[Post], output_dir: Path = OUTPUT_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"humoruniv_{timestamp}.json"
    data = []
    for p in posts:
        data.append({
            "community": p.community, "title": p.title, "url": p.url,
            "body": p.body, "images": p.images,
            "comments": [{"author": c.author, "text": c.text, "likes": c.likes} for c in p.comments],
            "views": p.views, "recommends": p.recommends, "collected_at": p.collected_at,
        })
    import json
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[humoruniv] Saved {len(posts)} posts to {path}")
    return path


if __name__ == "__main__":
    posts = collect()
    if posts:
        save(posts)
    else:
        print("[humoruniv] No posts collected")
