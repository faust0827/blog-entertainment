#!/usr/bin/env python3
"""승인 후 자동 공개 파이프라인 (dry-run 기본)."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--labels", help="라벨(쉼표 구분)")
    parser.add_argument("--dry-run", action="store_true", help="게이트만 점검, 발행하지 않음")
    args = parser.parse_args()

    if not args.file.is_file():
        print(f"파일 없음: {args.file}", file=sys.stderr)
        return 1

    cmd = [sys.executable, str(HERE / "publish.py"), str(args.file), "--check-only"]
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print("게이트 미통과 — 발행 차단", file=sys.stderr)
        return 3

    if args.dry_run or os.environ.get("AUTO_PUBLISH_ENABLED", "").strip() != "1":
        print("dry-run: 게이트 통과. AUTO_PUBLISH_ENABLED=1 설정 시 공개 발행합니다.")
        return 0

    cmd = [sys.executable, str(HERE / "publish.py"), str(args.file), "--publish", "--auto"]
    if args.labels:
        cmd += ["--labels", args.labels]
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())