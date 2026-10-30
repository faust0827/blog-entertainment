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
