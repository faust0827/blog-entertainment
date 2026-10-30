#!/usr/bin/env python3
"""아카라이브(arca.live) 베스트 라이브 크롤러 (requests + BeautifulSoup)."""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://arca.live"
BEST_URL = f"{BASE}/b/live"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


@dataclass
class Comment:
    author: str = ""
    text: str = ""
    likes: int = 0


@dataclass
class Post:
    community: str = "arca"
    title: str = ""
    url: str = ""
    body: str = ""
    images: list[str] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    views: int = 0
    recommends: int = 0
    collected_at: str = ""


def fetch(url):
    return requests.get(url, headers={"User-Agent": UA}, timeout=20)


def collect() -> list[Post]:
    posts = []
    r = fetch(BEST_URL)
    if r.status_code != 200:
        print(f"[arca] list fetch failed: {r.status_code}")
        return posts

    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    seen = set()
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if not re.search(r"/b/[^/]+/\d+", h):
            continue
        if h in seen:
            continue
        seen.add(h)
        full = h if h.startswith("http") else BASE + h
        title = a.get_text(strip=True)
        if len(title) < 3:
            continue
        links.append({"url": full, "title": title})
        if len(links) >= 12:
            break
    links = links[:8]
    print(f"[arca] Found {len(links)} candidate posts")

    for item in links:
        try:
            print(f"  Fetching: {item['title'][:50]}...")
            pr = fetch(item["url"])
            if pr.status_code != 200:
                print(f"  Error: status {pr.status_code}")
                continue
            soup = BeautifulSoup(pr.text, "html.parser")
            post = Post(url=item["url"], collected_at=datetime.now().isoformat())

            # title
            og = soup.find("meta", property="og:title")
            post.title = (og["content"].strip() if og and og.get("content") else item["title"])

            # body: article-content or article-body
            body_el = soup.select_one(".article-content, .article-body, article .content")
            if body_el:
                post.body = body_el.get_text(strip=True)[:1000]
            else:
                # fallback: og:description
                ogd = soup.find("meta", property="og:description")
                post.body = (ogd["content"].strip() if ogd and ogd.get("content") else "")[:1000]

            # images
            for im in soup.find_all("img"):
                src = im.get("src", "")
                if src.startswith("//"):
                    src = "https:" + src
                if src.startswith("http") and "arca.live" not in src and "icon" not in src:
                    if src not in post.images:
                        post.images.append(src)
            post.images = post.images[:5]

            # comments
            seen_c = set()
            for e in soup.select(".comment-item, .comment-content, .comment-wrapper"):
                t = e.get_text(strip=True)
                if not t or len(t) < 5 or t in seen_c or len(t) > 400:
                    continue
                seen_c.add(t)
                post.comments.append(Comment(text=t[:200]))
            post.comments = post.comments[:20]

            posts.append(post)
            print(f"    Body: {len(post.body)} chars, Images: {len(post.images)}, Comments: {len(post.comments)}")
            time.sleep(1)
        except Exception as e:
            print(f"  Error: {e}")

    return posts


def save(posts, output_dir=OUTPUT_DIR):
    import json
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"arca_{timestamp}.json"
    data = [{"community": p.community, "title": p.title, "url": p.url, "body": p.body,
             "images": p.images, "comments": [{"author": c.author, "text": c.text, "likes": c.likes} for c in p.comments],
             "views": p.views, "recommends": p.recommends, "collected_at": p.collected_at} for p in posts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[arca] Saved {len(posts)} posts to {path}")
    return path


if __name__ == "__main__":
    posts = collect()
    if posts:
        save(posts)
    else:
        print("[arca] No posts collected")
