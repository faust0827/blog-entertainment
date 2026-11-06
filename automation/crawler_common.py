#!/usr/bin/env python3
"""커뮤니티 크롤러 공통 데이터 구조."""
from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass
class Comment:
    author: str = ""
    text: str = ""
    likes: int = 0


@dataclass
class Post:
    community: str = ""
    title: str = ""
    url: str = ""
    body: str = ""
    images: list[str] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    views: int = 0
    recommends: int = 0
    collected_at: str = ""


HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}


def save_posts(posts, community, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"{community}_{timestamp}.json"
    data = []
    for p in posts:
        data.append({
            "community": p.community,
            "title": p.title,
            "url": p.url,
            "body": p.body,
            "images": p.images,
            "comments": [{"author": c.author, "text": c.text, "likes": c.likes} for c in p.comments],
            "views": p.views,
            "recommends": p.recommends,
            "collected_at": p.collected_at,
        })
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{community}] Saved {len(posts)} posts to {path}")
    return path


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _extract_title(soup: BeautifulSoup, fallback: str) -> str:
    for sel in ["meta[property='og:title']", "title", "h1", "h2.title", ".title", ".subject"]:
        if sel.startswith("meta"):
            el = soup.select_one(sel)
            if el and el.get("content"):
                t = _clean(el["content"])
                if t:
                    return t
        else:
            el = soup.select_one(sel)
            if el:
                t = _clean(el.get_text())
                if t and len(t) > 3:
                    return t
    return fallback


def _extract_body(soup: BeautifulSoup) -> str:
    best = ""
    for sel in ["article", "main", ".content", "#content", ".post-content", ".viewContent",
                ".article", ".read_body", ".board-content", ".entry-content", ".text", ".writing_view", ".view_content"]:
        for el in soup.select(sel):
            t = _clean(el.get_text())
            if len(t) > len(best) and len(t) < 20000:
                best = t
    if len(best) < 100:
        # collect paragraphs
        ps = [_clean(p.get_text()) for p in soup.find_all("p")]
        joined = " ".join(t for t in ps if t)
        if len(joined) > len(best):
            best = joined
    return best[:4000]


def _extract_images(soup: BeautifulSoup, base: str) -> list[str]:
    imgs = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src:
            full = urljoin(base, src)
            if full not in imgs:
                imgs.append(full)
    return imgs[:5]


def _extract_comments(soup: BeautifulSoup) -> list[Comment]:
    comments = []
    seen = set()
    selectors = [".comment", "#comment", ".reply", ".replies", "li.reply", "[class*='comment']"]
    for sel in selectors:
        for el in soup.select(sel):
            t = _clean(el.get_text())
            if 2 < len(t) < 500 and t not in seen:
                seen.add(t)
                comments.append(Comment(text=t))
    if not comments:
        # fallback: short paragraphs
        for p in soup.find_all("p"):
            t = _clean(p.get_text())
            if 2 < len(t) < 200 and t not in seen:
                seen.add(t)
                comments.append(Comment(text=t))
    return comments[:20]


def generic_collect(community: str, start_url: str, max_posts: int = 8) -> list[Post]:
    posts: list[Post] = []
    try:
        r = requests.get(start_url, headers=HEADERS, timeout=20)
        r.encoding = r.apparent_encoding or r.encoding
        r.raise_for_status()
    except Exception as e:
        print(f"[{community}] list load error: {e}")
        return posts

    soup = BeautifulSoup(r.text, "html.parser")
    links = []
    seen = set()
    for a in soup.find_all("a"):
        href = a.get("href")
        title = _clean(a.get_text())
        if not href or len(title) < 4:
            continue
        if href.startswith("javascript:") or href.startswith("#"):
            continue
        if re.search(r"login|join|signup|search|act=disp|category|event|notice", href):
            continue
        if not re.search(r"read|view|document|article|seq=|[nN]o=|wr_id=|/[0-9]{6,}", href):
            continue
        if any(k in title for k in ["공지", "필독", "이용 규칙", "규정", "이용약관"]):
            continue
        full = urljoin(start_url, href)
        if full in seen:
            continue
        seen.add(full)
        links.append((full, title))
    links = links[:20]
    print(f"[{community}] Found {len(links)} candidate posts")

    for url, fallback_title in links[:max_posts]:
        try:
            print(f"  Fetching: {fallback_title[:50]}...")
            rr = requests.get(url, headers=HEADERS, timeout=20)
            rr.encoding = rr.apparent_encoding or rr.encoding
            rr.raise_for_status()
            psoup = BeautifulSoup(rr.text, "html.parser")
            post = Post(url=url, community=community, collected_at=datetime.now().isoformat())
            post.title = _extract_title(psoup, fallback_title)
            post.body = _extract_body(psoup)
            post.images = _extract_images(psoup, url)
            post.comments = _extract_comments(psoup)
            if post.title and (len(post.body) > 10 or post.images or post.comments):
                posts.append(post)
                print(f"    Body: {len(post.body)} chars, Comments: {len(post.comments)}")
        except Exception as e:
            print(f"  Error: {e}")

    return posts


def generic_save(posts: list[Post], community: str, output_dir: Path) -> Path:
    return save_posts(posts, community, output_dir)

def generic_collect_playwright(community: str, start_url: str, max_posts: int = 8) -> list[Post]:
    """Playwright 기반 범용 크롤러 (JS 렌더링 사이트용)."""
    from playwright.sync_api import sync_playwright

    posts: list[Post] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        try:
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page.goto(start_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(4000)
        except Exception as e:
            print(f"[{community}] list load error: {e}")
            browser.close()
            return posts

        links = page.evaluate("""() => {
            const anchors = document.querySelectorAll('a');
            const seen = new Set();
            const result = [];
            for (const a of anchors) {
                const href = a.getAttribute('href') || '';
                const title = (a.textContent || '').trim();
                if (!href || title.length < 4) continue;
                if (/^javascript:|^#/i.test(href)) continue;
                if (/login|join|signup|search|act=disp|category|event|notice/i.test(href)) continue;
                if (/공지|필독|이용 규칙|규정|이용약관/.test(title)) continue;
                if (!/(read|view|document|article|seq=|[nN]o=|wr_id=|\\/[0-9]{6,})/i.test(href)) continue;
                const full = href.startsWith('http') ? href : (location.origin + (href.startsWith('/') ? '' : '/') + href);
                if (seen.has(full)) continue;
                seen.add(full);
                result.push({url: full, title: title});
            }
            return result.slice(0, 20);
        }""")
        print(f"[{community}] Found {len(links)} candidate posts")

        for item in links[:max_posts]:
            try:
                print(f"  Fetching: {item['title'][:50]}...")
                page.goto(item["url"], wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)

                post = Post(url=item["url"], community=community, collected_at=datetime.now().isoformat())

                try:
                    t = page.title() or ""
                    t = t.split("|")[0].split("-")[0].strip()
                    if t and len(t) > 3:
                        post.title = t
                except Exception:
                    pass
                if not post.title:
                    for sel in ["h1", "h2", ".title", ".subject", ".post-title"]:
                        try:
                            el = page.query_selector(sel)
                            if el:
                                txt = el.inner_text().strip()
                                if txt and len(txt) > 3:
                                    post.title = txt
                                    break
                        except Exception:
                            pass
                if not post.title:
                    post.title = item["title"]

                body = ""
                for sel in ["article", "main", ".content", "#content", ".post-content", ".viewContent",
                            ".article", ".read_body", ".board-content", ".entry-content", ".text", ".writing_view"]:
                    try:
                        el = page.query_selector(sel)
                        if el:
                            txt = el.inner_text().strip()
                            if len(txt) > len(body):
                                body = txt
                    except Exception:
                        pass
                if len(body) < 100:
                    try:
                        body = page.evaluate("""() => Array.from(document.querySelectorAll('p')).map(p=>p.innerText.trim()).filter(Boolean).join(' ')""")
                    except Exception:
                        body = ""
                post.body = (body or "").strip()[:4000]

                try:
                    imgs = page.query_selector_all("img")
                    post.images = [img.get_attribute("src") for img in imgs if img.get_attribute("src")][:5]
                except Exception:
                    pass

                comment_texts = []
                for sel in ["[class*='comment']", "[id*='comment']", ".reply", ".replies"]:
                    try:
                        els = page.query_selector_all(sel)
                        for el in els:
                            t = (el.inner_text() or "").strip()
                            if t and 2 < len(t) < 500 and t not in comment_texts:
                                comment_texts.append(t)
                    except Exception:
                        pass
                if not comment_texts:
                    try:
                        ps = page.query_selector_all("p")
                        for el in ps:
                            t = (el.inner_text() or "").strip()
                            if 2 < len(t) < 200 and t not in comment_texts:
                                comment_texts.append(t)
                    except Exception:
                        pass
                for text in comment_texts[:20]:
                    post.comments.append(Comment(text=text))

                if post.title and (len(post.body) > 10 or post.images or post.comments):
                    posts.append(post)
                    print(f"    Body: {len(post.body)} chars, Comments: {len(post.comments)}")
            except Exception as e:
                print(f"  Error: {e}")

        browser.close()
    return posts
