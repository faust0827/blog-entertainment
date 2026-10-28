#!/usr/bin/env python3
"""오늘의 유머 베스트글 크롤러 (Playwright 기반)."""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://www.todayhumor.co.kr"
BEST_URL = f"{BASE}/board/list.php?table=bestofbest"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@dataclass
class Comment:
    author: str = ""
    text: str = ""
    likes: int = 0


@dataclass
class Post:
    community: str = "todayhumor"
    title: str = ""
    url: str = ""
    body: str = ""
    images: list[str] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    views: int = 0
    recommends: int = 0
    collected_at: str = ""


def collect() -> list[Post]:
    """Playwright로 베스트 게시판 수집."""
    posts = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})

        # Best list
        page.goto(BEST_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # Extract post links
        links = page.evaluate("""() => {
            const anchors = document.querySelectorAll('a[href*="view.php"]');
            const seen = new Set();
            const result = [];
            for (const a of anchors) {
                const href = a.getAttribute('href');
                const title = a.textContent.trim();
                if (!href || !title || title.length < 5) continue;
                const fullUrl = href.startsWith('http') ? href : 'https://www.todayhumor.co.kr' + href;
                if (seen.has(fullUrl)) continue;
                seen.add(fullUrl);
                result.push({url: fullUrl, title: title});
            }
            return result.slice(0, 15);
        }""")

        print(f"[todayhumor] Found {len(links)} candidate posts")

        for item in links[:8]:
            try:
                print(f"  Fetching: {item['title'][:50]}...")
                page.goto(item["url"], wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(5000)  # Wait for comments to load via AJAX

                post = Post(url=item["url"], collected_at=datetime.now().isoformat())

                # Title
                title_el = page.query_selector("title")
                if title_el:
                    post.title = title_el.inner_text().replace("오늘의유머 - ", "").strip()

                # Body
                body_el = page.query_selector(".viewContent")
                if body_el:
                    post.body = body_el.inner_text().strip()

                # Images
                imgs = page.query_selector_all(".viewContent img")
                post.images = [img.get_attribute("src") for img in imgs if img.get_attribute("src")][:5]

                # Comments - extract from page using Python
                comment_texts = []
                try:
                    els = page.query_selector_all('[class*="memo"]')
                    for el in els:
                        t = (el.inner_text() or '').strip()
                        if t and 2 < len(t) < 500:
                            lines = [l.strip() for l in t.split('\\n') if l.strip()]
                            comment_text = lines[-1] if len(lines) > 1 else lines[0]
                            if comment_text and len(comment_text) > 2 and comment_text not in comment_texts:
                                comment_texts.append(comment_text)
                except Exception:
                    pass
                for text in comment_texts[:20]:
                    post.comments.append(Comment(text=text))

                if post.title and (len(post.body) > 10 or len(post.images) > 0 or len(post.comments) > 0):
                    posts.append(post)
                    print(f"    Body: {len(post.body)} chars, Comments: {len(post.comments)}")
            except Exception as e:
                print(f"  Error: {e}")

        browser.close()
    return posts


def save(posts: list[Post], output_dir: Path = OUTPUT_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"todayhumor_{timestamp}.json"
    data = []
    for p in posts:
        d = {"community": p.community, "title": p.title, "url": p.url,
             "body": p.body, "images": p.images,
             "comments": [{"author": c.author, "text": c.text, "likes": c.likes} for c in p.comments],
             "views": p.views, "recommends": p.recommends, "collected_at": p.collected_at}
        data.append(d)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[todayhumor] Saved {len(posts)} posts to {path}")
    return path


if __name__ == "__main__":
    posts = collect()
    if posts:
        save(posts)
    else:
        print("[todayhumor] No posts collected")
