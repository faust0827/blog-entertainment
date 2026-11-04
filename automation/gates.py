#!/usr/bin/env python3
"""품질 게이트 — 큐레이션 블로그용."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

MAX_QUOTE_CHARS = 500  # 원문 직접 인용 최대 500자
MAX_QUOTE_SENTENCES = 5  # 원문 직접 인용 최대 5문장
MIN_LENGTH = 1000  # 큐레이션은 1,000자 이상

PROFANITY_TERMS = [
    "시발", "씨발", "ㅅㅂ", "병신", "ㅂㅅ", "존나", "지랄",
    "개새", "개새끼", "미친놈", "미친년", "닥쳐", "꺼져",
    "애미", "애비", "좆", "fuck", "shit",
]

RAW_SLANG_TOKENS = ["ㅋㅋ", "ㄷㄷ", "ㄹㅇ", "ㅇㅈ", "ㅇㅋ"]


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
    if short_count > 12:
        return GateResult("댓글요약", False, f"짧은 문단 {short_count}개 — 댓글 원문 복사 의심")
    return GateResult("댓글요약", True, f"짧은 문단 {short_count}개")


def gate_value_add(content: str) -> GateResult:
    """AI 해설·분석 단락 1개 이상."""
    keywords = ["해설", "분석", "배경", "맥락", "의견", "정리하면", "의미", "시사점"]
    found = any(kw in content for kw in keywords)
    if not found:
        return GateResult("가치추가", False, "AI 해설·분석 단락 없음")
    return GateResult("가치추가", True, "가치 추가 확인")


def gate_seo_structure(content: str) -> GateResult:
    """SEO 구조: H2 2개 이상 + JSON-LD 구조화 데이터 존재."""
    import re
    h2_count = len(re.findall(r"<h2\b", content, re.I))
    has_jsonld = "application/ld+json" in content
    issues = []
    if h2_count < 2:
        issues.append(f"H2 {h2_count}개 (최소 2개)")
    if not has_jsonld:
        issues.append("JSON-LD 없음")
    if issues:
        return GateResult("SEO구조", False, "; ".join(issues))
    return GateResult("SEO구조", True, f"H2 {h2_count}개 + JSON-LD")


def gate_length(content: str) -> GateResult:
    """분량 1,000자 이상."""
    text = re.sub(r"<[^>]+>", "", content)
    length = len(text.strip())
    if length < MIN_LENGTH:
        return GateResult("분량", False, f"{length}자 (최소 {MIN_LENGTH}자)")
    return GateResult("분량", True, f"{length}자")


def gate_artifacts(content: str) -> GateResult:
    """파일 아티팩트·깨진 이미지 금지."""
    bad = []
    if '"""' in content:
        bad.append('trailing-quotes')
    if '(truncated)' in content:
        bad.append('truncated-marker')
    if 'data:image' in content or 'base64' in content:
        bad.append('base64-image')
    if bad:
        return GateResult("아티팩트", False, ", ".join(bad))
    return GateResult("아티팩트", True, "정상")


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


def gate_profanity(content: str) -> GateResult:
    """욕설·비속어 노출 금지."""
    found = [t for t in PROFANITY_TERMS if t in content]
    if found:
        return GateResult("비속어", False, f"비속어 {len(found)}건: {', '.join(found[:5])}")
    return GateResult("비속어", True, "위반 0건")


def gate_raw_slang(content: str) -> GateResult:
    """원문 댓글 은어·자음체 과다 노출 금지."""
    count = sum(content.count(tok) for tok in RAW_SLANG_TOKENS)
    if count >= 3:
        return GateResult("댓글은어", False, f"은어 토큰 {count}건 (최대 2건)")
    return GateResult("댓글은어", True, f"은어 토큰 {count}건")


def gate_nickname_exposure(content: str) -> GateResult:
    """커뮤니티 닉네임 직접 노출 금지."""
    import re
    patterns = [
        r'닉네임.{0,10}["“][^"”]{2,}["”]',
        r'["“][^"”]{2,}["”].{0,10}닉네임',
        r'라는\s*닉네임',
    ]
    hits = []
    for pat in patterns:
        hits.extend(re.findall(pat, content))
    if hits:
        return GateResult("닉네임", False, f"닉네임 노출 {len(hits)}건")
    return GateResult("닉네임", True, "위반 0건")


def run_gates(content: str) -> list[GateResult]:
    """모든 게이트 실행."""
    return [
        gate_banned_phrases(content),
        gate_length(content),
        gate_quote_length(content),
        gate_source_link(content),
        gate_comment_summary(content),
        gate_value_add(content),
        gate_seo_structure(content),
        gate_artifacts(content),
        gate_profanity(content),
        gate_raw_slang(content),
        gate_nickname_exposure(content),
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
