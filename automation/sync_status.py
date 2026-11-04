#!/usr/bin/env python3
"""머신 간 작업 공유 상태 점검."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MACHINE_ID = ROOT / ".machine_id"


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def main():
    machine = MACHINE_ID.read_text().strip() if MACHINE_ID.exists() else "(미설정)"
    print(f"머신: {machine}")
    print(f"브랜치: {run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])}")
    print(f"HEAD: {run(['git', 'rev-parse', '--short', 'HEAD'])}")
    unpushed = run(["git", "log", "--oneline", "origin/main..HEAD"])
    print("미push 커밋:")
    print(unpushed if unpushed else "  (없음)")
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"])
    print("미추적 파일:")
    print(untracked if untracked else "  (없음)")
    ledger = ROOT / "automation" / "schedule_ledger.json"
    if ledger.exists():
        import json
        data = json.loads(ledger.read_text(encoding="utf-8"))
        print(f"예약 ledger 항목: {len(data.get('entries', []))}건")
    url_map = ROOT / "automation" / "url_map.json"
    if url_map.exists():
        import json
        data = json.loads(url_map.read_text(encoding="utf-8"))
        print(f"url_map 항목: {len(data)}건")
    log = ROOT / "WORK_LOG.md"
    if log.exists():
        lines = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip().startswith("20")]
        print("최근 작업 로그:")
        for l in lines[-5:]:
            print("  " + l)


if __name__ == "__main__":
    main()
