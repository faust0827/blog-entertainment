#!/usr/bin/env python3
"""발행된 글의 검색엔진 색인 요청 안내 스크립트.

사용법:
  .venv/bin/python automation/submit_index.py https://issuedayissue.blogspot.com/2026/10/blog-post.html
  .venv/bin/python automation/submit_index.py --file posts/2026-wedding-grave-photo.html
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def extract_url_from_file(path: Path) -> str | None:
    html = path.read_text(encoding="utf-8")
    # canonical or og:url
    for pat in [r'<link rel="canonical" href="([^"]+)"', r'<meta property="og:url" content="([^"]+)"']:
        m = re.search(pat, html)
        if m:
            return m.group(1)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="색인 요청 안내")
    ap.add_argument("url", nargs="?", help="발행된 글 URL")
    ap.add_argument("--file", help="HTML 파일 경로 (URL 자동 추출)")
    args = ap.parse_args()

    url = args.url
    if args.file:
        url = extract_url_from_file(Path(args.file))
    if not url:
        print("URL을 입력하거나 --file로 HTML 파일을 지정하세요.", file=sys.stderr)
        return 2

    print("=" * 60)
    print("색인 요청 안내")
    print("=" * 60)
    print(f"\n대상 URL: {url}\n")

    print("[Google Search Console]")
    print("1. https://search.google.com/search-console 접속")
    print("2. 좌측 상단 URL 검사창에 위 URL 입력")
    print("3. '색인 생성 요청' 클릭")
    print(f"   직접 링크: https://search.google.com/search-console/inspect?resource_id=https%3A%2F%2Fissuedayissue.blogspot.com%2F&siteUrl=https%3A%2F%2Fissuedayissue.blogspot.com%2F&id={url}")
    print()

    print("[네이버 서치 어드바이저]")
    print("1. https://searchadvisor.naver.com 접속")
    print("2. '요청' → 'URL 제출'")
    print("3. 위 URL 입력 → 제출")
    print()

    print("[RSS 자동 수집 (네이버)]")
    print("네이버는 RSS를 자동 수집하므로, RSS 제출이 완료되어 있으면 별도 요청 불필요.")
    print(f"RSS: https://issuedayissue.blogspot.com/feeds/posts/default?alt=rss")
    print()
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
