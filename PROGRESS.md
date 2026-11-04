# 프로젝트 진행 기록

> 작업 머신: **X230** (이 문서의 모든 변경·발행 기록은 X230에서 수행)

## 2026-10-29 세팅 및 확장

### 환경
- [X230] Python 3.10.12
- [X230] `.venv` 생성 및 패키지 설치: requests, beautifulsoup4, openai, anthropic, playwright, google-api-python-client, google-auth-oauthlib, google-auth-httplib2
- [X230] Playwright Chromium 설치 완료
- [X230] Google Chrome `/usr/bin/google-chrome` 사용

### 자동화
- [X230] `automation/auth_setup.py` 추가 (Blogger OAuth)
- [X230] `automation/publish.py` 추가 (게이트·초안·공개·예약·갱신 지원)
- [X230] `automation/auto_post.py` 추가
- [X230] `automation/requirements.txt` 추가
- [X230] `automation/curate.py`에 `.env` 자동 로드 추가
- [X230] `automation/crawler_common.py` 공통 모듈 추가 (generic requests + Playwright 수집)
- [X230] 커뮤니티 크롤러 16개: todayhumor, dogdrip, fmkorea, theqoo, ruliweb, inven, ppomppu, mlbpark, clien, instiz, bobaedream, humoruniv, cook82, damoang, orbi, gasengi
- [X230] `automation/crawler.py` 통합 실행기 갱신

### Blogger 연결
- [X230] OAuth 인증 완료, `automation/token.json` 생성
- [X230] 대상 블로그: https://issuedayissue.blogspot.com/ (ID 5324449119197977039)
- [X230] `publish.py` `DEFAULT_BLOG_URL = "issuedayissue.blogspot.com"`

### 발행된 글
- [X230] https://issuedayissue.blogspot.com/2026/10/2-2.html
  - [X230] 제목: [화제] 2주째 아이 하나만 내려주고 2분 지켜본 태권도 사범 — 커뮤니티 반응 모음
  - [X230] 게이트 6/6 통과, LIVE
- [X230] https://issuedayissue.blogspot.com/2026/10/blog-post_28.html
  - [X230] 제목: [화제] 원당역 역무원 칼부림 사건 — 코레일 안전관리 부실과 커뮤니티 반응
  - [X230] 게이트 6/6 통과, LIVE

### 운영 메모
- [X230] AI API 미사용, 글은 수동 작성
- [X230] 교차 큐레이션: 여러 커뮤니티에서 같은 주제를 찾아 반응을 모아 작성
- [X230] 쿠팡 파트너스 글에는 제휴 고지 문구 필수
- [X230] 쿠팡 파트너스와 애드센스 병행 검토 중

### 추가 발행
- [X230] https://issuedayissue.blogspot.com/2026/10/2l6.html
  - [X230] 제목: [리뷰] 녹물 나온 아파트에서 생수로 바꾼 이유 — 제주삼다수 그린 무라벨 2L×6
  - [X230] 게이트 6/6 통과, LIVE
  - [X230] 쿠팡 파트너스 고지 문구 포함

### 광고 코드 반영
- [X230] 쿠팡 파트너스 JS 배너 (300×250 carousel, trackingCode AF3610050)를 모든 posts/*.html에 삽입
- [X230] 기존 공개 글 14개에 광고 코드 반영 완료
- [X230] publish.py에 광고 코드 자동 삽입 로직 추가 (발행 시 본문 끝에 자동 추가)
- [X230] 출처 링크 target="_blank" 적용 (모든 posts/*.html 및 publish.py 자동 주입)
- [X230] 기존 공개 글 15개에 출처 링크 새창 열기 반영 완료
- [X230] PROGRESS.md에 머신 표시 [X230] 적용 및 별도 기록 파일 통합

### 추가 발행 5
- [X230] https://issuedayissue.blogspot.com/2026/10/inven.html
  - [X230] 제목: 나만의 약국을 꿈꾸며 공부 열심히한 약사 — inven 반응 모음
  - [X230] 게이트 6/6 통과, LIVE

### 추가 발행 4
- [X230] https://issuedayissue.blogspot.com/2026/10/blog-post_663.html
  - [X230] 제목: 족발 시키다 알게된 불륜썰 — 개드립 반응 모음
  - [X230] 게이트 6/6 통과, LIVE
- [X230] https://issuedayissue.blogspot.com/2026/10/86.html
  - [X230] 제목: 86년생이면 아줌마 소리 들을 나이야?? — 개드립 반응 모음
  - [X230] 게이트 6/6 통과, LIVE
- [X230] https://issuedayissue.blogspot.com/2026/10/3843.html
  - [X230] 제목: 서울대 공대 학점 3.8/4.3인데도 서류 탈락 — 취업시장 근황과 커뮤니티 반응
  - [X230] 게이트 6/6 통과, LIVE
- [X230] https://issuedayissue.blogspot.com/2026/10/119-2.html
  - [X230] 제목: 소아청소년과 근황 — 119명 모집에 2명 지원, 커뮤니티 반응
  - [X230] 게이트 6/6 통과, LIVE
- [X230] https://issuedayissue.blogspot.com/2026/10/humoruniv_0271298328.html
  - [X230] 제목: 가스파드 탕수육 실제 후기 — humoruniv 반응 모음
  - [X230] 게이트 6/6 통과, LIVE
- [X230] https://issuedayissue.blogspot.com/2026/10/humoruniv_01686489683.html
  - [X230] 제목: 엄마가 돌아가셨어 — humoruniv 반응 모음
  - [X230] 게이트 6/6 통과, LIVE

### 추가 발행 2
- [X230] https://issuedayissue.blogspot.com/2026/10/blog-post_645.html
  - [X230] 제목: [화제] 디시 싱갤 글로 서울우유에 고소당한 썰 — 커뮤니티 반응 모음
  - [X230] 게이트 6/6 통과, LIVE

### 추가 발행 3
- [X230] https://issuedayissue.blogspot.com/2026/10/20-13.html
  - [X230] 제목: [화제] 20살에 13살 많은 점장에게 고백한 사연 — 커뮤니티 반응 모음
  - [X230] 게이트 6/6 통과, LIVE
- [X230] https://issuedayissue.blogspot.com/2026/10/humoruniv.html
  - [X230] 제목: [화제] 꿈꾸던 약국을 직접 차린 약사님 — humoruniv 반응 모음
  - [X230] 게이트 6/6 통과, LIVE

### AdSense 대비 점검·보강 (2026-11-02)
- [X230] 필수 페이지 4개 발행: 소개(/p/issueissue.html), 개인정보처리방침(/p/issueissue_01303993325.html), 문의(/p/issueissue_01623452620.html), 이용약관(/p/issueissue_0102540285.html)
- [X230] `publish.py`에 누락된 `import re` 추가
- [X230] `gates.py`에 아티팩트 검사 게이트 추가 (trailing quotes, truncated marker, base64 이미지)
- [X230] `posts/2026-disability-meal-anonymous-donor.html` 깨진 base64 이미지 제거 및 오타 수정, 라이브 글 갱신
- [X230] `posts/*.html` trailing `"""` 아티팩트 16개 일괄 제거
- [X230] README의 존재하지 않는 `templates/blog-layout.xml` 참조 수정
- 수동 필요: Blogger 메뉴에 페이지 링크 추가, robots.txt sitemap을 issuedayissue.blogspot.com으로 수정, Search Console 등록

## 2026-11-04 [X230] 자동 remediation

- [X230] posts/*.html 23개에 JSON-LD(Article) 주입 (SEO구조 게이트 통과)
- [X230] 비속어·은어 토큰 22개 글에서 중립화 ([비속어] 치환·은어 제거)
- [X230] 전체 63개 글 10/10 게이트 통과 확인
- [X230] 머신 간 공유 체계 구축 (WORK_LOG, sync_status, SYNC 프로토콜)
