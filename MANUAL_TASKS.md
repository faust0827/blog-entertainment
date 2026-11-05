# Blogger 수동 작업 가이드 (IssueIssue 블로그)

대상: https://issuedayissue.blogspot.com/ (Blogger 관리자)
목적: AdSense 승인 준비 + SEO + 라벨 정리

## 0. 사전 확인
- Google 계정으로 Blogger 관리자 로그인
- 블로그 선택: IssueIssue
- 좌측 메뉴 "설정" / "레이아웃" / "페이지" / "글" 이동 방법 숙지

---

## 1. 페이지 링크를 메뉴에 추가 (필수)

1. Blogger 관리자 → 좌측 "페이지" 클릭
2. 아래 4개 페이지가 있는지 확인 (없으면 "새 페이지"로 생성)
   - 소개 (about)
   - 문의 (contact)
   - 개인정보처리방침 (privacy)
   - 이용약관 (terms)
   - (이미 `pages/` 폴더에 HTML이 있으므로 내용 복사 가능)
3. 좌측 "레이아웃" 클릭
4. 상단 메뉴 영역(Header / Pages gadget)의 "편집" 클릭
5. "페이지 추가" → 위 4개 페이지 선택 → 저장
6. "저장" (레이아웃) 클릭
7. 블로그 홈에서 메뉴에 4개 링크가 보이는지 확인

---

## 2. 각 글의 검색 설명(Search Description) 입력 (필수)

Blogger는 HTML meta description을 무시하므로 글 설정에서 직접 입력해야 합니다.
먼저 블로그 레벨에서 검색 설명 기능을 켜야 글 편집 화면에 "검색 설명" 항목이 나타납니다.

### 2-0. 검색 설명 기능 활성화 (1회)
1. Blogger 관리자 → "설정" → "검색 환경설정" (Search preferences)
2. "메타 태그" (Meta tags) → "설명" (Description) → "사용" (Yes/Enabled)
3. "저장" 클릭

### 2-1. 글별 검색 설명 입력
1. Blogger 관리자 → 좌측 "글" 클릭
2. 글 목록에서 하나 선택 → "수정" 클릭
3. 우측 설정 패널 "검색 설명" (Search Description) 항목 찾기
4. `automation/search_descriptions.txt`에서 해당 글 제목 찾아 설명 복사·붙여넣기
5. "완료" / "게시" 또는 "업데이트" 클릭
6. 53개 라이브 글 + 예약 10개 글 모두 반복

팁: 5~10개씩 나눠서 진행. 하루 10개 목표.

---

## 3. 라벨(카테고리) 정리

자동 라벨링 완료 상태:
- 디지털생활: 비밀번호 관리자, 클라우드 저장소, AI 이미지 도구, 노트북 발열, 스마트폰 배터리, PDF/와이파이/부가세/겨울방한/제주삼다수
- 인터넷트렌드: 커뮤니티 반응 글 전체

추가 정리 (선택):
1. "글" → 라벨별 필터로 확인
2. 커뮤니티 글 중 "사회이슈" 성격은 라벨 변경 가능
3. 라벨 3개 권장: 사회이슈 / 인터넷트렌드 / 생활정보

---

## 4. robots.txt sitemap 수정

1. Blogger 관리자 → "설정" → "크롤러 및 색인 생성" (Crawlers and indexing)
2. "robots.txt 사용자 정의" (Custom robots.txt) 활성화
3. 아래 내용 입력 (sitemap URL 확인 후):

```
User-agent: *
Disallow: /search
Allow: /
Sitemap: https://issuedayissue.blogspot.com/sitemap.xml
```

4. "저장" 클릭

---

## 5. Google Search Console 등록

1. https://search.google.com/search-console 접속
2. "속성 추가" → URL 접두어: https://issuedayissue.blogspot.com/
3. 소유권 확인: HTML 태그 방식 선택 → 메타 태그를 Blogger "테마 → HTML 편집" `<head>`에 삽입 → 확인
4. "sitemap" 메뉴 → `https://issuedayissue.blogspot.com/sitemap.xml` 제출
5. `index_urls.txt`의 URL을 "URL 검사"로 하루 10~20개씩 색인 요청

---

## 6. AdSense 연결 (publisher ID 발급 후)

1. https://www.google.com/adsense 가입
2. 사이트 추가: issuedayissue.blogspot.com
3. 사이트 소유권 확인: AdSense가 제공하는 메타 태그/ads.txt 안내 따름
4. Blogger "수익 창출" (Earnings) 메뉴에서 AdSense 계정 연결
5. publisher ID (ca-pub-XXXXXXXX)를 개발자에게 전달 → 자동으로 모든 posts/*.html에 광고 코드 삽입

주의: 현재 콘텐츠 상태로는 신청 금지 (전략 문서 참고). 디지털 생활 가이드 10~15개 축적 후 신청.

---

## 7. 발행 속도 관리

- 하루 1건 발행 (예약 발행 사용)
- 현재 예약: 11/10~11/14 (5건)
- 새 글은 `automation/curate.py` 또는 수동 작성 후 `publish.py --schedule` 사용
- 게이트 11/11 통과 확인 후 발행

---

## 8. (선택) Blogger 라벨 메뉴

1. 레이아웃 → 라벨 가젯 편집
2. 표시할 라벨 선택: 디지털생활, 인터넷트렌드
3. 저장

---

## 현재 자동화 상태 (2026-11-05)

- posts: 82개, 가이드 글 24개
- 품질 게이트: 82/82 통과 (11/11)
- 예약 발행: 11/03~11/29 (하루 1건)
- MAX_DAILY: 1 (automation/filter.py)
- 미커밋 변경: 없음 (최신 커밋 d366e6c)

## 체크리스트 요약

- [ ] 메뉴에 4개 페이지 링크
- [ ] 검색 설명 82개 입력
- [ ] 라벨 3개로 정리
- [ ] robots.txt sitemap 수정
- [ ] Search Console 등록 + sitemap 제출
- [ ] 색인 요청 (하루 10~20건)
- [ ] AdSense 가입 (가이드 15개+ 및 수동 조치 완료 후)
- [ ] 발행 속도 하루 1건 유지
EOF
echo done