#!/usr/bin/env python3
"""'글써줘' 한 번에 실행: 크롤링 → 큐레이션 → 게이트 → 초안 발행.

사용법:
  .venv/bin/python automation/auto_post.py          # 전체 파이프라인
  .venv/bin/python automation/auto_post.py --no-crawl  # 크롤링 건너뛰기
  .venv/bin/python automation/auto_post.py --publish   # 게이트 통과 시 공개 발행 (주의)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
POSTS = ROOT / "posts"
RAW = ROOT / "data" / "raw"
PYTHON = str(ROOT / ".venv" / "bin" / "python")


def run(cmd, **kw):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, **kw)


def latest_post() -> Path | None:
    posts = sorted(POSTS.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    return posts[0] if posts else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-crawl", action="store_true")
    ap.add_argument("--publish", action="store_true", help="공개 발행 (기본은 초안)")
    args = ap.parse_args()

    # 1. 크롤링
    if not args.no_crawl:
        r = run([PYTHON, str(HERE / "crawler.py")], cwd=str(ROOT))
        if r.returncode != 0:
            print("크롤링 실패", file=sys.stderr)

    # 2. 큐레이션 (API 키 있을 때만)
    import os
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"):
        r = run([PYTHON, str(HERE / "curate.py")], cwd=str(ROOT))
        if r.returncode != 0:
            print("큐레이션 실패", file=sys.stderr)
    else:
        print("API 키 없음 → 큐레이션 건너뜀 (기존 posts/ 사용)")

    # 3. 최신 글 선택
    post = latest_post()
    if not post:
        print("발행할 글이 없습니다.", file=sys.stderr)
        return 1
    print(f"\n대상 글: {post}")

    # 4. 게이트 점검
    r = run([PYTHON, str(HERE / "publish.py"), str(post), "--check-only"], cwd=str(ROOT))
    if r.returncode != 0:
        print("게이트 미통과 → 발행 중단", file=sys.stderr)
        return 3

    # 5. 발행
    cmd = [PYTHON, str(HERE / "publish.py"), str(post)]
    if args.publish:
        cmd += ["--publish", "--reviewed"]
    else:
        cmd += ["--draft"]
    r = run(cmd, cwd=str(ROOT))
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
