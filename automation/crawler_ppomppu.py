#!/usr/bin/env python3
"""뽐뿌(ppomppu.co.kr) 자유게시판 크롤러 (requests 기반)."""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import requests

BASE = "https://www.ppomppu.co.kr"
LIST_URL = f"{BASE}/zboard/zboard.php?id=freeboard"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


@dataclass
class Comment:
    author: str = ""
    text: str = ""
    likes: int = 0


@dataclass
class Post:
    community: str = "ppomppu"
    title: str = ""
    url: str = ""
    body: str = ""
    images: list[str] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    views: int = 0
    recommends: int = 0
    collected_at: str = ""


def fetch(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.encoding = "euc-kr"
    return r


def collect() -> list[Post]:
    posts = []
    r = fetch(LIST_URL)
    if r.status_code != 200:
        print(f"[ppomppu] list fetch failed: {r.status_code}")
        return posts

    # post links
    links = []
    seen = set()
    for m in re.finditer(r'href="(view\.php\?id=freeboard[^"]*no=\d+[^"]*)"', r.text):
        h = m.group(1)
        if h in seen:
            continue
        seen.add(h)
        full = BASE + "/zboard/" + h
        links.append(full)
        if len(links) >= 12:
            break
    links = links[:8]
    print(f"[ppomppu] Found {len(links)} candidate posts")

    for url in links:
        try:
            print(f"  Fetching: {url[-20:]}...")
            pr = fetch(url)
            if pr.status_code != 200:
                print(f"  Error: status {pr.status_code}")
                continue
            html = pr.text
            post = Post(url=url, collected_at=datetime.now().isoformat())

            m = re.search(r'<meta property="og:title" content="(.*?)"', html)
            post.title = (m.group(1) if m else "").strip()

            m = re.search(r'<meta name="description" content="(.*?)"', html)
            post.body = (m.group(1) if m else "").strip()

            # images
            for im in re.finditer(r'<img[^>]+src="(https?://[^"]+)"', html):
                src = im.group(1)
                if "ppomppu" not in src and src not in post.images:
                    post.images.append(src)
            post.images = post.images[:5]

            # comments: collect text from table cells roughly
            seen_c = set()
            for m in re.finditer(r'<td[^>]*>(.*?)</td>', html, re.S):
                t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                t = " ".join(t.split())
                if len(t) < 5 or len(t) > 300 or t in seen_c:
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
    path = output_dir / f"ppomppu_{timestamp}.json"
    data = [{"community": p.community, "title": p.title, "url": p.url, "body": p.body,
             "images": p.images, "comments": [{"author": c.author, "text": c.text, "likes": c.likes} for c in p.comments],
             "views": p.views, "recommends": p.recommends, "collected_at": p.collected_at} for p in posts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ppomppu] Saved {len(posts)} posts to {path}")
    return path


if __name__ == "__main__":
    posts = collect()
    if posts:
        save(posts)
    else:
        print("[ppomppu] No posts collected")
