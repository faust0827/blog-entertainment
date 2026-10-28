# 커뮤니티 큐레이션 블로그

## 한 줄 요약

커뮤니티(오늘의 유머, 개 drip, FM코리아) 인기글을 큐레이션하여 블로그로 발행하는 완전 자동화 프로젝트.

- 플랫폼: Blogger (무료 호스팅 + AdSense)
- 주제: 연예/이슈
- 운영: 크롤링 → AI 큐레이션 → 품질 게이트 → 예약 발행 (완전 자동)
- 수익: Google AdSense

## 파일 구조

```
blog-entertainment/
├── AGENTS.md              # OpenCode 프로젝트 지침 (페르소나 + 규칙)
├── README.md              # 이 문서
├── keywords.md            # 주제/키워드 추적
├── templates/
│   └── post-template.md   # 큐레이션 글 구조 + 페르소나 + 프롬프트
├── automation/
│   ├── crawler.py         # 커뮤니티 인기글 수집 통합 실행기
│   ├── crawler_todayhumor.py  # 오늘의 유머 크롤러
│   ├── filter.py          # 민감 콘텐츠 필터링
│   ├── curate.py          # AI 큐레이션 파이프라인
│   └── gates.py           # 품질 게이트 (기본 6종 + 큐레이션 전용 4종)
├── posts/                 # 생성된 HTML 글
├── pages/                 # 소개·개인정보처리방침
├── tests/                 # 단위 테스트
└── data/
    └── raw/               # 크롤링 원본 데이터 (JSON)
```

## 환경 설정

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4 openai anthropic playwright google-api-python-client google-auth-oauthlib
playwright install chromium
```

### Blogger 블로그 생성 (최초 1회)

1. https://www.blogger.com → Google 계정 로그인 → "새 블로그"
2. 제목·주소 설정 (예: `entertainment-curate.blogspot.com`) → "만들기"
3. Google Cloud Console (https://console.cloud.google.com) → 새 프로젝트 → Blogger API v3 사용 설정
4. OAuth 클라이언트 ID 생성 (데스크톱 앱) → `client_secret_*.json` 다운로드 → 프로젝트 폴더에 복사
5. `python automation/auth_setup.py` 실행 → 브라우저에서 인증 → `token.json` 생성
6. `automation/publish.py`의 `DEFAULT_BLOG_URL`을 새 블로그 주소로 수정
7. Blogger 관리 → 테마 → 백업/다운로드 (원본 백업) → 복원/업로드 → `templates/blog-layout.xml` 선택
8. 소개·개인정보처리방침 페이지 생성, 라벨(카테고리) 구성

### 환경변수

```bash
export OPENAI_API_KEY="sk-..."       # 또는
export ANTHROPIC_API_KEY="sk-ant-..." # 둘 중 하나
```

### Blogger 인증

```bash
python automation/auth_setup.py  # 최초 1회 (기존 todayhumor 방식 재사용)
```

## 사용법

### 1. 크롤링

```bash
python automation/crawler.py
```

### 2. AI 큐레이션 + 발행

```bash
python automation/curate.py  # HTML 생성
python automation/publish.py posts/slug.html --check-only  # 게이트 점검
python automation/publish.py posts/slug.html --schedule 2026-11-07T10:30:00+09:00 --labels 연예이슈  # 예약 발행
```

### 3. 자동화 (cron)

```bash
# 매일 06:00 크롤링 + 큐레이션 + 예약 발행
0 6 * * * cd /path/to/blog-entertainment && .venv/bin/python automation/crawler.py && .venv/bin/python automation/curate.py
```

## 법적 가드레일

1. 원문 인용 5문장(500자) 이하
2. 댓글은 요약만 (원문 복사 금지)
3. 출처 URL 필수
4. AI 해설·분석 단락 필수
5. 민감 콘텐츠 제외 (정치·종교·성인·혐오·개인정보)
6. 저작권 이미지 제외 (링크만)
7. 킬스위치: 분쟁 시 즉시 비공개

## 큐레이션 대상 커뮤니티

| 커뮤니티 | 인기 기준 | 난이도 |
|---|---|---|
| 오늘의 유머 | 추천 30+ | 중간 |
| 웃긴대학 | 일간 베스트 | 중간 |
| 개 drip | 추천 50+ | 중간 |
| FM코리아 | 추천 100+ | 낮음 |

## 수익 모델

- Google AdSense (주 수익)
- 제휴 링크 (보조 수익)

## 주의사항

- 크롤링은 법적 그레이존입니다. robots.txt 준수 + 요청 간격 3초 이상
- AI API 비용: 월 5~15만 원
- 애드센스 승인: "가치 있는 콘텐츠" 기준 충족 필요
- 저작권 분쟁 시 즉시 비공개 처리
PY