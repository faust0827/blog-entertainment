#!/usr/bin/env python3
"""이미지 OCR 모듈 — EasyOCR 기반 (무료, 한국어 지원)."""
from __future__ import annotations

import io
import warnings
warnings.filterwarnings("ignore")

import requests
from PIL import Image

_reader = None


def get_reader():
    """EasyOCR Reader 싱글턴 (첫 호출 시 모델 로드)."""
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["ko", "en"], gpu=False, verbose=False)
    return _reader


def ocr_image_url(url: str, max_chars: int = 1000) -> str:
    """이미지 URL을 다운로드하여 OCR 텍스트를 반환. 실패 시 빈 문자열."""
    if not url:
        return ""
    try:
        resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        reader = get_reader()
        results = reader.readtext(resp.content, detail=0, paragraph=True)
        text = "\n".join(str(r) for r in results).strip()
        if len(text) > max_chars:
            text = text[:max_chars] + "…"
        return text
    except Exception as e:
        print(f"  [OCR] 실패 ({url[:60]}...): {e}")
        return ""


def ocr_images(urls: list[str], max_chars: int = 500) -> str:
    """여러 이미지 URL을 OCR하여 하나의 텍스트로 합침."""
    parts = []
    for i, url in enumerate(urls[:3], 1):
        text = ocr_image_url(url)
        if text:
            parts.append(f"[이미지 {i} 텍스트] {text}")
    return "\n".join(parts)


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if url:
        print(ocr_image_url(url))
    else:
        print("Usage: python ocr.py <image_url>")
