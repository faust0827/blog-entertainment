#!/usr/bin/env python3
"""커뮤니티 댓글 반응 정리 도구.

사용법:
  .venv/bin/python automation/comment_digest.py --keyword "태권도" --top 5
  .venv/bin/python automation/comment_digest.py --keyword "원당역" --output data/digest_wondang.md
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"

META_PATTERNS = [
    re.compile(r"\d{4}-\d{2}-\d{2}"),
    re.compile(r"\d{1,3}\.\d{1,3}\.\*\*\*"),
    re.compile(r"추천\s*\d+"),
    re.compile(r"^\s*\(\d{4}"),
    re.compile(r"댓글\s*\d+개"),
    re.compile(r"댓글 더 보기|새 댓글 확인"),
]


def clean_comment(text: str) -> str:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    kept = []
    for ln in lines:
        if any(p.search(ln) for p in META_PATTERNS):
            continue
        if len(ln) < 3:
            continue
        kept.append(ln)
    # Prefer the longest meaningful line if multiple
    if not kept:
        return ""
    if len(kept) == 1:
        return kept[0]
    return max(kept, key=len)


def load_latest_raw():
    by_comm = {}
    for f in sorted(RAW_DIR.glob("*_20*.json")):
        comm = f.name.split("_")[0]
        if comm == "combined":
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        by_comm[comm] = data
    return by_comm


def find_posts(by_comm, keyword: str):
    result = {}
    for comm, posts in by_comm.items():
        matched = []
        for p in posts:
            title = p.get("title", "")
            body = p.get("body", "")
            if keyword.lower() in title.lower() or keyword.lower() in body.lower():
                matched.append(p)
        if matched:
            result[comm] = matched
    return result


def digest_post(post: dict, top: int) -> list[str]:
    raw_comments = [c.get("text", "") for c in post.get("comments", [])]
    cleaned = []
    seen = set()
    for rc in raw_comments:
        c = clean_comment(rc)
        if not c or c in seen:
            continue
        if len(c) < 4:
            continue
        seen.add(c)
        cleaned.append(c)
    return cleaned[:top]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    by_comm = load_latest_raw()
    matched = find_posts(by_comm, args.keyword)

    lines = [f"# 댓글 반응 정리: {args.keyword}", ""]
    if not matched:
        lines.append("일치하는 게시글을 찾지 못했습니다.")
    for comm in sorted(matched):
        lines.append(f"## {comm}")
        for post in matched[comm][:2]:
            lines.append(f"- 제목: {post.get('title','')}")
            lines.append(f"- URL: {post.get('url','')}")
            lines.append(f"- 추천/댓글 수: 추천 {post.get('recommends',0)} · 댓글 {len(post.get('comments',[]))}")
            lines.append("")
            lines.append("대표 반응:")
            for i, c in enumerate(digest_post(post, args.top), 1):
                lines.append(f"{i}. {c}")
            lines.append("")
        lines.append("")

    text = "\n".join(lines)
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"\n저장: {args.output}")


if __name__ == "__main__":
    main()