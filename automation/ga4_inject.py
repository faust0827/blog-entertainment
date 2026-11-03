#!/usr/bin/env python3
"""Blogger 테마 XML에 GA4 (gtag.js) 스크립트를 삽입하는 도구.

사용법:
  .venv/bin/python automation/ga4_inject.py --id G-XXXXXXXXXX --theme templates/blog-layout.xml --out /tmp/theme-with-ga4.xml
  .venv/bin/python automation/ga4_inject.py --id G-XXXXXXXXXX --theme ~/Downloads/theme.xml --out ~/Downloads/theme-ga4.xml
"""
import argparse
import sys
from pathlib import Path

SNIPPET_TEMPLATE = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{gid}');
</script>'''


def inject(theme_path: Path, measurement_id: str) -> str:
    xml = theme_path.read_text(encoding="utf-8")
    if measurement_id in xml:
        print("이미 삽입되어 있습니다.")
        return xml
    snippet = SNIPPET_TEMPLATE.format(gid=measurement_id)
    # Insert before </head>
    if "</head>" not in xml:
        print("</head> 태그를 찾을 수 없습니다. 테마 XML 형식을 확인하세요.", file=sys.stderr)
        sys.exit(1)
    xml = xml.replace("</head>", snippet + "\n</head>", 1)
    return xml


def main() -> int:
    ap = argparse.ArgumentParser(description="Blogger 테마에 GA4 스크립트 삽입")
    ap.add_argument("--id", required=True, help="GA4 측정 ID (G-XXXXXXXXXX)")
    ap.add_argument("--theme", required=True, help="입력 테마 XML 파일")
    ap.add_argument("--out", required=True, help="출력 테마 XML 파일")
    args = ap.parse_args()

    if not args.id.startswith("G-"):
        print("측정 ID는 G-로 시작해야 합니다 (예: G-XXXXXXXXXX).", file=sys.stderr)
        return 2

    theme_path = Path(args.theme).expanduser()
    if not theme_path.is_file():
        print(f"테마 파일을 찾을 수 없습니다: {theme_path}", file=sys.stderr)
        return 1

    out_path = Path(args.out).expanduser()
    result = inject(theme_path, args.id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result, encoding="utf-8")
    print(f"GA4 스크립트 삽입 완료: {out_path}")
    print(f"측정 ID: {args.id}")
    print("다음 단계: Blogger 대시보드 → 테마 → 백업/복원 → 복원/업로드 → 위 파일 선택")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
