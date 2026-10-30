#!/usr/bin/env python3
"""AI 큐레이션 파이프라인 — 커뮤니티 글을 블로그 글로 변환."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from filter import filter_posts

# AI API 설정 (환경변수에서 읽음)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

CURATE_PROMPT = """당신은 커뮤니티 큐레이션 블로그의 글 작성자입니다.
대상 독자: 커뮤니티에 관심 있는 일반인.

# 고정 페르소나 — 혼합형 (친근한 큐레이터 + 트렌드 리포터 + 팩트체크 에디터)
- 화자: 커뮤니티 화제를 빠르게 전달하면서도 출처와 수치를 정확히 짚어 주는 큐레이터.
- 제목/첫 문단(트렌드 리포터 톤): "화제", "실시간", "지금 커뮤니티에서" 등 시의성 있는 표현으로 클릭·공유를 유도. 과장·낚시성 표현 금지.
- 본문 요약(친근한 큐레이터 톤): 커뮤니티 원글을 그대로 복사하지 않고 핵심만 쉽게 요약. 독자가 "이게 뭐야?"라고 느끼지 않도록 배경과 맥락 추가.
- 댓글 반응: "긍정/부정/논쟁" 비율과 대표 반응만 요약 (원문 복사 금지).
- 해설·분석(팩트체크 에디터 톤): 출처 URL과 수치·날짜를 명시, 공식 자료 기준 정확 서술. "~로 보입니다", "~로 알려졌습니다" 등 확인된 표현 사용.
- 공무원·전문가 자격이나 직접 경험을 꾸며내지 않는다.
- AI 말투 금지: "요즘 현대인들은", "마지막으로 정리하자면", "도움이 되셨기를 바랍니다", "지금까지 ~을 자세히 살펴보았습니다", "오늘은 ~에 대해 알아보겠습니다".
- 이미지 직접 삽입 금지. 원본 이미지 URL 링크는 허용 (출처 참고용).
- 이미지 텍스트를 인용할 때 'OCR', '추출', '텍스트 인식' 등의 메타 표현 사용 금지. 자연스럽게 내용으로만 서술.
- SEO 규칙:
  1. 제목에 핵심 키워드를 앞쪽에 배치.
  2. 메타 description에 핵심 키워드 포함 (30~120자).
  3. 첫 문단에 검색 의도에 대한 직접 답변.
  4. H2 소제목에 검색 키워드 변형 포함.
  5. FAQ 섹션은 검색 의도 기반 질문으로 구성.
- 문체: ~합니다/~입니다 체 유지 (제목/첫 문단에서만 짧고 강한 어조 허용).

제공 자료:
- 커뮤니티: {community}
- 원제: {title}
- 원문 요약: {body_summary}
- 이미지 텍스트 (OCR): {image_text}
- 댓글 수: {comment_count}개
- 대표 반응: {top_comments}

필수 규칙:
1. 구조는 템플릿 준수 — 첫 문단에 핵심 요약
2. 원글 요약은 3~5문장 이내. 직접 인용은 최소화.
3. 댓글은 반응 비율 + 대표 반응 요약 (원문 복사 금지)
4. AI 해설·분석 단락 1개 이상 (배경·맥락·의견)
5. 출처 URL 반드시 포함
6. 금지 표현: "요즘 현대인들은", "마지막으로 정리하자면", "도움이 되셨기를 바랍니다"
7. 장황하게 쓰지 않기 — 짧은 문단, 핵심만
분량: 1,000~2,000자

출력 형식: HTML (DOCTYPE, head, body 포함). 본문은 <p>, <h2>, <h3>, <ul>, <ol>, <table> 태그 사용.
마지막에 <p><strong>확인일: YYYY-MM-DD</strong> · 출처: <a href="URL">커뮤니티명</a></p> 포함.
"""


def curate_post(post: dict) -> str | None:
    """단일 게시글 큐레이션."""
    community = post.get("community", "unknown")
    title = post.get("title", "")
    body = post.get("body", "")[:1000]
    comments = post.get("comments", [])
    comment_count = len(comments)
    top_comments = "\n".join(f"- {c.get('text', '')[:100]}" for c in comments[:5])
    url = post.get("url", "")
    images = post.get("images", [])
    image_text = ""
    if images:
        try:
            from ocr import ocr_images
            image_text = ocr_images(images)
            if image_text:
                print(f"  OCR: {len(image_text)} chars extracted")
        except Exception as e:
            print(f"  OCR 실패: {e}")

    prompt = CURATE_PROMPT.format(
        community=community,
        title=title,
        body_summary=body,
        image_text=image_text or "(이미지 없음 또는 OCR 실패)",
        comment_count=comment_count,
        top_comments=top_comments,
    )
    
    # Try OpenAI first, then Anthropic
    if OPENAI_API_KEY:
        return _call_openai(prompt, title, url)
    elif ANTHROPIC_API_KEY:
        return _call_anthropic(prompt, title, url)
    else:
        print("  API 키가 설정되지 않았습니다. OPENAI_API_KEY 또는 ANTHROPIC_API_KEY 환경변수를 설정하세요.")
        return None


def _call_openai(prompt: str, title: str, url: str) -> str | None:
    """OpenAI API 호출."""
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 커뮤니티 큐레이션 블로그 글 작성자입니다. HTML만 출력하세요."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"  OpenAI API error: {e}")
        return None


def _call_anthropic(prompt: str, title: str, url: str) -> str | None:
    """Anthropic API 호출."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return response.content[0].text
    except Exception as e:
        print(f"  Anthropic API error: {e}")
        return None


def curate_batch(raw_dir: str = None, existing_titles: list[str] | None = None) -> list[tuple[str, str]]:
    """크롤링된 데이터를 큐레이션하여 HTML 파일 생성."""
    if raw_dir is None:
        raw_dir = str(Path(__file__).resolve().parent.parent / "data" / "raw")
    
    raw_path = Path(raw_dir)
    if not raw_path.exists():
        print(f"Raw data directory not found: {raw_dir}")
        return []
    
    # Load latest combined file
    combined_files = sorted(raw_path.glob("combined_*.json"), reverse=True)
    if not combined_files:
        print("No combined data files found")
        return []
    
    data = json.loads(combined_files[0].read_text(encoding="utf-8"))
    print(f"Loaded {len(data)} posts from {combined_files[0].name}")
    
    # Filter
    filtered = filter_posts(data, existing_titles)
    print(f"After filtering: {len(filtered)} posts")
    
    # Curate
    results = []
    for i, post in enumerate(filtered):
        print(f"\n[{i+1}/{len(filtered)}] Curating: {post.get('title', '')[:50]}...")
        html = curate_post(post)
        if html:
            results.append((post.get("title", ""), html))
            print(f"  OK ({len(html)} chars)")
        else:
            print(f"  FAILED")
    
    return results


if __name__ == "__main__":
    results = curate_batch()
    print(f"\nCurated {len(results)} posts")
