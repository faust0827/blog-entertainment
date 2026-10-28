#!/usr/bin/env python3
"""커뮤니티 콘텐츠 필터링."""
from __future__ import annotations

import json
import re
from pathlib import Path

SENSITIVE_KEYWORDS = [
    "정치", "선거", "대통령", "국회", "여당", "야당",
    "종교", "교회", "절", "성경", "불경",
    "성인", "야동", "섹스", "음란",
    "혐오", "혐한", "혐일", "혐중", "인종",
    "개인정보", "주민번호", "전화번호", "계좌",
    "자살", "자해", "극단적",
]

MAX_DAILY = 3


def is_sensitive(title: str, body: str) -> bool:
    """민감 콘텐츠 여부 판별."""
    text = (title + " " + body).lower()
    return any(kw in text for kw in SENSITIVE_KEYWORDS)


def is_duplicate(title: str, existing_titles: list[str], threshold: float = 0.6) -> bool:
    """제목 유사도 기반 중복 판별."""
    title_lower = title.lower()
    for existing in existing_titles:
        # Simple word overlap
        words1 = set(title_lower.split())
        words2 = set(existing.lower().split())
        if not words1 or not words2:
            continue
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        if overlap >= threshold:
            return True
    return False


def filter_posts(posts: list[dict], existing_titles: list[str] | None = None) -> list[dict]:
    """필터링: 민감 콘텐츠 제외, 중복 제거, 일일 한도."""
    existing = existing_titles or []
    result = []
    for post in posts:
        title = post.get("title", "")
        body = post.get("body", "")
        if is_sensitive(title, body):
            continue
        if is_duplicate(title, existing + [p.get("title", "") for p in result]):
            continue
        result.append(post)
        if len(result) >= MAX_DAILY:
            break
    return result


if __name__ == "__main__":
    # Test with sample data
    sample = [
        {"title": "오늘 유머 베스트 1", "body": "재미있는 내용"},
        {"title": "정치 관련 글", "body": "정치 이야기"},
        {"title": "오늘 유머 베스트 2", "body": "또 다른 재미있는 내용"},
    ]
    filtered = filter_posts(sample)
    print(f"Input: {len(sample)}, Output: {len(filtered)}")
    for p in filtered:
        print(f"  - {p['title']}")
