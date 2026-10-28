#!/usr/bin/env python3
"""품질 게이트 — 큐레이션 블로그용."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

MAX_QUOTE_CHARS = 500  # 원문 직접 인용 최대 500자
MAX_QUOTE_SENTENCES = 5  # 원문 직접 인용 최대 5문장
MIN_LENGTH = 1000  # 큐레이션은 1,000자 이상


@dataclass
class GateResult:
    name: str
    passed: bool
    message: str


def gate_quote_length(content: str) -> GateResult:
    """원문 직접 인용 500자 이하."""
    # Blockquote or quoted text detection
    quotes = re.findall(r'<blockquote[^>]*>(.*?)</blockquote>', content, re.S)
    quote_text = " ".join(re.sub(r"<[^>]+>", "", q) for q in quotes)
    if len(quote_text) > MAX_QUOTE_CHARS:
        return GateResult("인용길이", False, f"원문 인용 {len(quote_text)}자 (최대 {MAX_QUOTE_CHARS}자)")
    return GateResult("인용길이", True, f"원문 인용 {len(quote_text)}자")


def gate_source_link(content: str) -> GateResult:
    """출처 URL 1개 이상 포함."""
    links = re.findall(r'href="(https?://[^"]+)"', content)
    external = [l for l in links if "blogspot.com" not in l and "localhost" not in l]
    if not external:
        return GateResult("출처링크", False, "출처 URL 없음")
    return GateResult("출처링크", True, f"출처 {len(external)}건")


def gate_comment_summary(content: str) -> GateResult:
    """댓글 원문 복사 금지 (요약만 허용)."""
    # Check for patterns that look like raw comments (short, no analysis)
    # Simple heuristic: if there are 3+ consecutive short paragraphs without analysis
    paragraphs = [p.strip() for p in re.findall(r'<p[^>]*>(.*?)</p>', content, re.S) if p.strip()]
    short_count = sum(1 for p in paragraphs if len(p) < 80)
    if short_count > 5:
        return GateResult("댓글요약", False, f"짧은 문단 {short_count}개 — 댓글 원문 복사 의심")
    return GateResult("댓글요약", True, f"짧은 문단 {short_count}개")


def gate_value_add(content: str) -> GateResult:
    """AI 해설·분석 단락 1개 이상."""
    keywords = ["해설", "분석", "배경", "맥락", "의견", "정리하면", "의미", "시사점"]
    found = any(kw in content for kw in keywords)
    if not found:
        return GateResult("가치추가", False, "AI 해설·분석 단락 없음")
    return GateResult("가치추가", True, "가치 추가 확인")


def gate_length(content: str) -> GateResult:
    """분량 1,000자 이상."""
    text = re.sub(r"<[^>]+>", "", content)
    length = len(text.strip())
    if length < MIN_LENGTH:
        return GateResult("분량", False, f"{length}자 (최소 {MIN_LENGTH}자)")
    return GateResult("분량", True, f"{length}자")


def gate_banned_phrases(content: str) -> GateResult:
    """AI 말투 금지."""
    banned = [
        "요즘 현대인들은", "마지막으로 정리하자면", "도움이 되셨기를 바랍니다",
        "지금까지 ~을 자세히 살펴보았습니다", "오늘은 ~에 대해 알아보겠습니다",
    ]
    found = [p for p in banned if p in content]
    if found:
        return GateResult("금지어", False, f"금지 표현 {len(found)}건: {', '.join(found)}")
    return GateResult("금지어", True, "위반 0건")


def run_gates(content: str) -> list[GateResult]:
    """모든 게이트 실행."""
    return [
        gate_banned_phrases(content),
        gate_length(content),
        gate_quote_length(content),
        gate_source_link(content),
        gate_comment_summary(content),
        gate_value_add(content),
    ]


def failed(results: list[GateResult]) -> list[GateResult]:
    return [r for r in results if not r.passed]


def format_results(results: list[GateResult], path: str = "") -> str:
    lines = [f"[게이트] {path}"]
    for r in results:
        mark = "✅" if r.passed else "❌"
        lines.append(f"  {mark} {r.name} — {r.message}")
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    status = "통과" if passed == total else "발행 차단"
    lines.append(f"▶ 게이트 {passed}/{total} {status}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python gates.py <html_file>")
        sys.exit(1)
    content = Path(sys.argv[1]).read_text(encoding="utf-8")
    results = run_gates(content)
    print(format_results(results, sys.argv[1]))
    if failed(results):
        sys.exit(3)
PY