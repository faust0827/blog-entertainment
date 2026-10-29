#!/usr/bin/env python3
"""더쿠 인기글 크롤러 (Playwright 기반)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crawler_common import generic_collect, generic_save, Post

COMMUNITY = "theqoo"
START_URL = "https://theqoo.net/hot"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def collect() -> list[Post]:
    return generic_collect(COMMUNITY, START_URL, max_posts=8)


def save(posts, output_dir: Path = OUTPUT_DIR) -> Path:
    return generic_save(posts, COMMUNITY, output_dir)


if __name__ == "__main__":
    posts = collect()
    if posts:
        save(posts)
    else:
        print(f"[{COMMUNITY}] No posts collected")
