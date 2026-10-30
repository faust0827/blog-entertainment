#!/usr/bin/env python3
"""커뮤니티 크롤러 통합 실행기."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crawler_todayhumor import collect as collect_todayhumor, save as save_todayhumor
from crawler_humoruniv import collect as collect_humoruniv, save as save_humoruniv
from crawler_dogdrip import collect as collect_dogdrip, save as save_dogdrip
from crawler_fmkorea import collect as collect_fmkorea, save as save_fmkorea
from crawler_theqoo import collect as collect_theqoo, save as save_theqoo
from crawler_ruliweb import collect as collect_ruliweb, save as save_ruliweb
from crawler_clien import collect as collect_clien, save as save_clien
from crawler_ppomppu import collect as collect_ppomppu, save as save_ppomppu
from crawler_bobaedream import collect as collect_bobaedream, save as save_bobaedream
from crawler_instiz import collect as collect_instiz, save as save_instiz
from crawler_inven import collect as collect_inven, save as save_inven
from crawler_mlbpark import collect as collect_mlbpark, save as save_mlbpark
from crawler_arca import collect as collect_arca, save as save_arca

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def main():
    all_posts = []
    
    print("=== 오늘의 유머 ===")
    try:
        posts = collect_todayhumor()
        all_posts.extend(posts)
        if posts:
            save_todayhumor(posts)
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== 웃긴대학 ===")
    try:
        posts = collect_humoruniv()
        all_posts.extend(posts)
        if posts:
            save_humoruniv(posts)
    except Exception as e:
        print(f"  Error: {e}")

    for name, col, sav in [
        ("개드립", collect_dogdrip, save_dogdrip),
        ("FM코리아", collect_fmkorea, save_fmkorea),
        ("더쿠", collect_theqoo, save_theqoo),
        ("루리웹", collect_ruliweb, save_ruliweb),
        ("클리앙", collect_clien, save_clien),
        ("뽐뿌", collect_ppomppu, save_ppomppu),
        ("보배드림", collect_bobaedream, save_bobaedream),
        ("인스티즈", collect_instiz, save_instiz),
        ("인벤", collect_inven, save_inven),
        ("엠팍", collect_mlbpark, save_mlbpark),
        ("아카라이브", collect_arca, save_arca),
    ]:
        print(f"\n=== {name} ===")
        try:
            posts = col()
            all_posts.extend(posts)
            if posts:
                sav(posts)
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n=== 총 수집: {len(all_posts)}건 ===")
    
    # Save combined
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
