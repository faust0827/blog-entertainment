# 동기화 기록 (Sync Log)

## 2026-10-30 — 다중 컴퓨터 작업 공유 시작

- **머신**: y40 (이 컴퓨터)
- **원격 저장소**: https://github.com/faust0827/blog-entertainment.git
- **push 완료**: `580ab44..6c9bf82 main -> main`
- **로컬 HEAD = 원격 origin/main**: `6c9bf82`

### 공유되는 것 (Git 추적)
- 코드: `automation/*.py`, `templates/`, `tests/`
- 글: `posts/*.html` (38개)
- 문서: `AGENTS.md`, `README.md`, `SETUP.md`, `SEO_TODO.md`, `TUNING_TODO.md`
- 스킬: `.opencode/skills/blog-writing.md` (force-add)
- 작업 목록/진행 기록

### 공유되지 않는 것 (머신별, .gitignore)
- `automation/client_secret.json` (OAuth 비밀)
- `automation/token.json` (인증 토큰)
- `.venv/` (Python 가상환경)
- `data/` (크롤링 원본, 저작권)
- `.machine_id` (머신 식별자)

### 다른 컴퓨터에서 작업 시작 절차
1. `git pull origin main`
2. `SETUP.md` 참고하여 가상환경/의존성/OAuth 설정
3. `git config user.name "머신이름"` (머신별 식별)
4. 작업 후 `git push origin main`

### 워크플로우
```
작업 시작: git pull
작업 중: git commit (로컬)
작업 종료: git push
```

---

## 2026-10-30 16:15 — 작업 공유 완료 (push)

- **머신**: y40
- **push**: `b3122b4..73e49c9 main -> main`
- **로컬 HEAD = 원격**: `73e49c9`
- **총 커밋**: 95개 (모두 원격에 반영됨)

### 이번 세션에서 추가된 작업
- 아카라이브(arca.live) 크롤러 추가 (13개 커뮤니티)
- OCR 모듈 (EasyOCR) + curate.py 연동
- A+B 통합 큐레이션 (group_by_topic + 커뮤니티별 반응)
- 제목에서 괄호 접두어 제거 ([화제], [정보] 등)
- 내부 링크 자동 삽입 (url_map.json)
- SEO 태그 자동 삽입 (JSON-LD, OG, Canonical)
- GA4 연동 도구 (ga4_inject.py)
- 색인 요청 URL 목록 (index_urls.txt, 27개)
- 30+개 글 발행 (모두 LIVE)
- SETUP.md, SYNC.md, SEO_TODO.md, TUNING_TODO.md 문서

### 다른 컴퓨터에서 작업 시작
```bash
git pull origin main
# SETUP.md 참고하여 환경 설정
```

---

## 머신 태그 & 세션 프로토콜 (2026-11-04 추가)

### 머신 태그
- 커밋 메시지 접두어: `[X230]`, `[y40]` 등 (각 머신 고유 태그).
- `PROGRESS.md` 기록도 동일 태그 사용.

### 세션 시작 체크리스트
1. `git pull origin main`
2. `python automation/sync_status.py` (머신 id, 미push 커밋, 미추적 파일, ledger 건수 확인)
3. `tail -n 15 WORK_LOG.md` + `git log --oneline -10` 으로 다른 머신 작업 파악
4. 미push/미커밋 잔여물이 있으면 먼저 정리(커밋 또는 `wip/<머신>` 브랜치 push) 후 진행

### 세션 종료 체크리스트
1. 품질 게이트·테스트 실행
2. 의도한 파일만 `git add`
3. 커밋: `git commit -m "[태그] scope: 설명"`
4. `WORK_LOG.md`에 항목 append (커밋 해시 포함)
5. `git add WORK_LOG.md && git commit --amend --no-edit` 또는 별도 커밋
6. `git push origin main` (실패 시 `git pull --rebase` 후 재push)

### 미완성 작업 공유
- 중단 시 `wip/<머신>` 브랜치에 커밋+push하여 다른 머신이 fetch로 확인 가능.
- main에는 완료된 작업만 병합.

### 공유 자산 (git-tracked)
- `automation/schedule_ledger.json` — 예약 발행 이력 (중복 방지)
- `automation/url_map.json` — 내부 링크 매핑
- `pages/`, `posts/`, `index_urls.txt`, `WORK_LOG.md`, `SYNC.md`
