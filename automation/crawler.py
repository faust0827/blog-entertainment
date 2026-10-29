#!/usr/bin/env python3
"""커뮤니티 크롤러 통합 실행기."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

COMMUNITIES = [
    "crawler_todayhumor",
    "crawler_dogdrip",
    "crawler_fmkorea",
    "crawler_theqoo",
    "crawler_ruliweb",
    "crawler_inven",
    "crawler_ppomppu",
    "crawler_mlbpark",
    "crawler_clien",
    "crawler_instiz",
    "crawler_bobaedream",
    "crawler_humoruniv",
    "crawler_cook82",
    "crawler_damoang",
    "crawler_orbi",
    "crawler_gasengi",
]


def main():
    all_posts = []

    for mod_name in COMMUNITIES:
        name = mod_name.replace("crawler_", "")
        print(f"\n=== {name} ===")
        try:
            mod = importlib.import_module(mod_name)
            posts = mod.collect()
            all_posts.extend(posts)
            if posts:
                mod.save(posts)
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n=== 총 수집: {len(all_posts)}건 ===")

    if all_posts:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined = OUTPUT_DIR / f"combined_{timestamp}.json"
        combined.write_text(
            json.dumps([{"community": p.community, "title": p.title, "url": p.url,
                        "body": p.body[:500], "comment_count": len(p.comments),
                        "collected_at": p.collected_at} for p in all_posts],
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Combined saved: {combined}")


if __name__ == "__main__":
    main()