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
