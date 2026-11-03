# 블로그 프로젝트 — 처음부터 끝까지 세팅 가이드

> 이 문서는 **코딩을 처음 접하는 사람**도 따라할 수 있도록 작성되었습니다.
> 모든 단계를 순서대로 진행하세요. 중간에 막히면 해당 단계의 "문제 해결" 섹션을 확인하세요.

---

## 목차

1. [사전 준비 (프로그램 설치)](#1-사전-준비-프로그램-설치)
2. [프로젝트 다운로드](#2-프로젝트-다운로드)
3. [Python 가상환경 만들기](#3-python-가상환경-만들기)
4. [필요한 패키지 설치](#4-필요한-패키지-설치)
5. [Google Cloud Console 설정 (Blogger 연동)](#5-google-cloud-console-설정-blogger-연동)
6. [Blogger 블로그 만들기](#6-blogger-블로그-만들기)
7. [OAuth 인증 (token.json 생성)](#7-oauth-인증-tokenjson-생성)
8. [AI API 키 설정 (글 자동 생성용)](#8-ai-api-키-설정-글-자동-생성용)
9. [발행 테스트](#9-발행-테스트)
10. [일상 사용법](#10-일상-사용법)
11. [문제 해결 (FAQ)](#11-문제-해결-faq)

---

## 1. 사전 준비 (프로그램 설치)

### 1-1. Python 설치 확인
터미널(명령 프롬프트)을 열고 입력:
```bash
python3 --version
```
`Python 3.10` 이상이 나와야 합니다. 안 나오면:
- **Ubuntu/Debian**: `sudo apt install python3 python3-venv python3-pip`
- **macOS**: `brew install python3`
- **Windows**: https://www.python.org/downloads/ 에서 다운로드 (설치 시 "Add to PATH" 체크)

### 1-2. Git 설치 확인
```bash
git --version
```
안 나오면:
- **Ubuntu/Debian**: `sudo apt install git`
- **macOS**: `brew install git` 또는 Xcode Command Line Tools
- **Windows**: https://git-scm.com/download/win

### 1-3. Google Chrome 설치
크롤러가 Chrome을 사용합니다.
- **Ubuntu/Debian**: `sudo apt install google-chrome-stable` (또는 .deb 다운로드)
- **macOS**: https://www.google.com/chrome/
- **Windows**: https://www.google.com/chrome/

설치 확인:
```bash
which google-chrome
# /usr/bin/google-chrome 이 나오면 OK
```

---

## 2. 프로젝트 다운로드

### Git으로 클론 (권장)
```bash
git clone <저장소 URL> blog-entertainment
cd blog-entertainment
```

### 또는 ZIP 다운로드
1. GitHub 페이지에서 "Code → Download ZIP"
2. 압축 해제 후 폴더로 이동

---

## 3. Python 가상환경 만들기

가상환경은 이 프로젝트 전용 Python 환경입니다. 시스템 Python과 분리되어 안전합니다.

```bash
cd blog-entertainment
python3 -m venv .venv
```

가상환경 활성화:
```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

활성화되면 프롬프트 앞에 `(.venv)`가 표시됩니다.

---

## 4. 필요한 패키지 설치

```bash
pip install requests beautifulsoup4 openai anthropic playwright google-api-python-client google-auth-oauthlib
```

Playwright 브라우저 설치:
```bash
playwright install chromium
```

---

## 5. Google Cloud Console 설정 (Blogger 연동)

이 단계가 가장 중요합니다. Blogger에 글을 발행하려면 Google OAuth 인증이 필요합니다.

### 5-1. Google Cloud 프로젝트 생성
1. https://console.cloud.google.com 접속 → Google 계정 로그인
2. 상단 프로젝트 선택 드롭다운 → **"새 프로젝트"**
3. 프로젝트 이름 입력 (예: `blog-entertainment`) → **만들기**
4. 생성된 프로젝트가 선택되었는지 확인

### 5-2. Blogger API v3 활성화
1. 좌측 메뉴 → **"API 및 서비스" → "라이브러리"**
2. 검색창에 **"Blogger API"** 입력
3. **"Blogger API v3"** 클릭 → **"사용" (Enable)** 클릭

### 5-3. OAuth 동의 화면 설정
1. 좌측 메뉴 → **"API 및 서비스" → "OAuth 동의 화면"**
2. 사용자 유형: **"외부"** 선택 → **만들기**
3. 앱 정보 입력:
   - 앱 이름: `Entertainment Blog Publisher`
   - 사용자 지원 이메일: 본인 이메일
   - 개발자 연락처: 본인 이메일
4. **저장 후 계속**
5. 범위(Scopes) 단계:
   - **"범위 추가 또는 삭제"** 클릭
   - 검색창에 `blogger` 입력 → `https://www.googleapis.com/auth/blogger` 체크
   - 안 보이면 "수동으로 범위 추가"에 `https://www.googleapis.com/auth/blogger` 입력
   - **업데이트** → **저장 후 계속**
6. 테스트 사용자 단계:
   - **"+ 사용자 추가"** → 본인 Gmail 주소 입력 (예: `faust0827@gmail.com`)
   - **저장 후 계속**
7. 요약 확인 → **"대시보드로 돌아가기"**

> ⚠️ **중요**: 테스트 사용자에 본인 이메일을 반드시 등록해야 합니다. 등록하지 않으면 "액세스 차단됨" 오류가 발생합니다.

### 5-4. OAuth 클라이언트 ID 생성
1. 좌측 메뉴 → **"API 및 서비스" → "사용자 인증 정보"**
2. **"+ 사용자 인증 정보 만들기" → "OAuth 클라이언트 ID"**
3. 애플리케이션 유형: **"데스크톱 앱"** 선택
4. 이름: `blog-entertainment-desktop`
5. **만들기** → **"JSON 다운로드"**
6. 다운로드된 파일을 프로젝트의 `automation/` 폴더에 복사:
   ```bash
   mv ~/Downloads/client_secret_*.json automation/client_secret.json
   chmod 600 automation/client_secret.json
   ```

---

## 6. Blogger 블로그 만들기

1. https://www.blogger.com 접속 → Google 계정 로그인
2. **"새 블로그"** 클릭
3. 제목 입력 (예: `커뮤니티 큐레이션 블로그`)
4. 주소 설정 (예: `issuedayissue`) → `issuedayissue.blogspot.com`
5. 테마 선택 → **만들기**
6. 생성된 블로그 URL을 기억해 두세요

---

## 7. OAuth 인증 (token.json 생성)

```bash
cd blog-entertainment
.venv/bin/python automation/auth_setup.py
```

진행:
1. 스크립트가 로컬 서버(포트 8080)를 띄우고 인증 URL을 출력합니다.
2. 브라우저에서 해당 URL을 열고 Google 계정으로 로그인
3. "Blogger API 접근 허용" 동의
4. 인증 완료 → `automation/token.json` 자동 생성
5. 연결된 블로그 목록 출력

출력 예:
```
연결된 블로그:
  - 이름: IssueIssue
    URL : https://issuedayissue.blogspot.com/
    ID  : 5324449119197977039
```

### 발행 대상 블로그 설정
`automation/publish.py` 파일을 열어서 `DEFAULT_BLOG_URL`을 본인 블로그 주소로 수정:
```python
DEFAULT_BLOG_URL = "issuedayissue.blogspot.com"  # ← 본인 블로그 주소
```

---

## 8. AI API 키 설정 (글 자동 생성용)

글을 AI로 자동 생성하려면 API 키가 필요합니다. (없어도 수동 글 작성은 가능)

### OpenAI (권장)
1. https://platform.openai.com/api-keys 접속
2. **"Create new secret key"** → 키 복사
3. 환경변수 설정:
   ```bash
   # Linux / macOS (~/.bashrc 또는 ~/.zshrc에 추가)
   export OPENAI_API_KEY="sk-..."

   # Windows (PowerShell)
   $env:OPENAI_API_KEY = "sk-..."
   ```

### Anthropic (대안)
1. https://console.anthropic.com/ 접속
2. API Keys → Create Key
3. `export ANTHROPIC_API_KEY="sk-ant-..."`

---

## 9. 발행 테스트

### 9-1. 게이트 점검 (API 미사용)
```bash
.venv/bin/python automation/publish.py posts/2026-disability-meal-anonymous-donor.html --check-only
```
결과: `▶ 게이트 6/6 통과` 가 나오면 OK.

### 9-2. 초안 저장
```bash
.venv/bin/python automation/publish.py posts/2026-disability-meal-anonymous-donor.html --draft
```
Blogger에 초안으로 저장됩니다. Blogger 대시보드에서 확인 가능.

### 9-3. 공개 발행
```bash
.venv/bin/python automation/publish.py posts/2026-disability-meal-anonymous-donor.html --publish --reviewed
```

### 9-4. 크롤링 테스트
```bash
.venv/bin/python automation/crawler.py
```
`data/raw/` 폴더에 JSON 파일이 생성되면 OK.

---

## 10. 일상 사용법

### 글 작성 (AI 자동)
```bash
# 1. 크롤링
.venv/bin/python automation/crawler.py

# 2. AI 큐레이션 (HTML 글 생성)
.venv/bin/python automation/curate.py

# 3. 게이트 점검
.venv/bin/python automation/publish.py posts/<파일명>.html --check-only

# 4. 발행 (한 번에)
.venv/bin/python automation/auto_post.py
```

### 글 작성 (수동)
1. `templates/post-template.md` 읽기
2. OpenCode에서 "글써줘" 요청 → 페르소나 자동 적용
3. `posts/YYYY-slug.html` 저장
4. 게이트 점검 → 발행

### 발행 명령어 모음
```bash
# 초안 저장
.venv/bin/python automation/publish.py posts/slug.html --draft

# 예약 발행 (2026-11-07 10:30)
.venv/bin/python automation/publish.py posts/slug.html --schedule 2026-11-07T10:30:00+09:00 --labels 연예이슈

# 공개 발행
.venv/bin/python automation/publish.py posts/slug.html --publish --reviewed

# 게이트 점검만
.venv/bin/python automation/publish.py posts/slug.html --check-only
```

### 자동화 (cron)
```bash
# 매일 06:00 크롤링 + 큐레이션
0 6 * * * cd /path/to/blog-entertainment && .venv/bin/python automation/crawler.py && .venv/bin/python automation/curate.py
```

---

## 11. 문제 해결 (FAQ)

### "python: 명령을 찾을 수 없음"
→ `python3`를 사용하세요. 또는 Python을 설치하세요 (1-1 참조).

### "client_secret.json 없음"
→ Google Cloud Console에서 OAuth 클라이언트 ID를 생성하고 JSON을 `automation/` 폴더에 `client_secret.json` 이름으로 저장하세요 (5-4 참조).

### "토큰이 유효하지 않습니다"
→ `automation/token.json`을 삭제하고 `auth_setup.py`를 다시 실행하세요.

### "액세스 차단됨: 테스트 사용자 미등록"
→ Google Cloud Console → OAuth 동의 화면 → 테스트 사용자에 본인 이메일 추가 (5-3 참조).

### "연결된 블로그가 없습니다"
→ https://www.blogger.com 에서 블로그를 먼저 만드세요 (6 참조).

### "HttpError 403: Access Not Configured"
→ Blogger API v3가 활성화되지 않았습니다 (5-2 참조).

### 크롤러가 0건 수집
→ 사이트 구조가 변경되었을 수 있습니다. 해당 크롤러 파일을 확인하세요.

### 게이트 미통과
→ `--check-only` 출력에서 ❌ 항목을 확인하고 해당 문제를 수정하세요. (분량 부족, 금지어, 출처 누락 등)

### Playwright 설치 실패
→ `playwright install chromium`이 실패하면 `playwright install` (전체 브라우저)를 시도하세요.

### Chrome을 찾을 수 없음
→ 크롤러의 `executable_path='/usr/bin/google-chrome'`를 실제 Chrome 경로로 수정하세요. `which google-chrome`로 확인.

---

## 파일 구조 요약

```
blog-entertainment/
├── AGENTS.md              # AI 에이전트 지침 (페르소나 등)
├── README.md              # 프로젝트 개요
├── SETUP.md               # 이 문서 (세팅 가이드)
├── keywords.md            # 주제/키워드 추적
├── templates/
│   ├── post-template.md   # 글 구조 + 페르소나
│   └── blog-layout.xml    # Blogger 레이아웃
├── automation/
│   ├── crawler.py         # 통합 크롤러 실행기
│   ├── crawler_*.py       # 개별 커뮤니티 크롤러 (12개)
│   ├── filter.py          # 민감 콘텐츠 필터
│   ├── curate.py          # AI 큐레이션
│   ├── gates.py           # 품질 게이트
│   ├── publish.py         # Blogger 발행
│   ├── auth_setup.py      # OAuth 인증
│   └── auto_post.py       # 원클릭 파이프라인
├── posts/                 # 생성된 HTML 글
├── tests/                 # 단위 테스트
├── data/raw/              # 크롤링 원본 (gitignore)
└── .venv/                 # Python 가상환경 (gitignore)
```

---

## Google Analytics 4 (GA4) 연동 (선택)

1. https://analytics.google.com → "측정 시작" → 계정/속성 생성
2. "웹" 선택 → URL: `https://issuedayissue.blogspot.com/`
3. "측정 ID" (G-XXXXXXXXXX) 복사
4. Blogger 대시보드 → **테마 → HTML 편집** → `</head>` 직전에 아래 코드 삽입:
   ```html
   <!-- Google tag (gtag.js) -->
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag(){dataLayer.push(arguments);}
     gtag('js', new Date());
     gtag('config', 'G-XXXXXXXXXX');
   </script>
   ```
5. **저장** → 24~48시간 후 GA4 대시보드에서 데이터 확인

---

## 빠른 참조 (치트시트)

```bash
# 가상환경 활성화
source .venv/bin/activate

# 크롤링
.venv/bin/python automation/crawler.py

# AI 큐레이션
.venv/bin/python automation/curate.py

# 게이트 점검
.venv/bin/python automation/publish.py posts/<파일>.html --check-only

# 초안 발행
.venv/bin/python automation/publish.py posts/<파일>.html --draft

# 공개 발행
.venv/bin/python automation/publish.py posts/<파일>.html --publish --reviewed

# 예약 발행
.venv/bin/python automation/publish.py posts/<파일>.html --schedule 2026-11-07T10:30:00+09:00 --labels 연예이슈

# 원클릭 (글써줘)
.venv/bin/python automation/auto_post.py
```
