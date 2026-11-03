# SEO 최적화 작업 목록

> 중간에 끊겨도 이 파일을 확인하여 이어서 진행할 수 있습니다.
> 완료된 항목은 `[x]`로 표시하고, 커밋 해시를 기록합니다.

## 작업 목록

- [x] **1. templates/post-template.md에 SEO 태그 블록 추가**
  - Open Graph, Canonical, JSON-LD(Article) 태그 블록
  - 커밋: 8150c18

- [x] **2. automation/curate.py CURATE_PROMPT에 SEO 지시 추가**
  - 제목 키워드 앞쪽 배치, 메타 description 키워드 포함, 첫 문단 직접 답변, H2 키워드 변형, FAQ 검색 의도 기반
  - 커밋: 4207d11

- [x] **3. automation/publish.py에 SEO 태그 자동 삽입**
  - parse_html에서 title/description 추출 → JSON-LD 자동 삽입 (_inject_seo)
  - 커밋: 6d622db

- [x] **4. 기존 글(posts/)에 SEO 태그 소급 적용**
  - 3개 기존 글에 OG + JSON-LD 소급 적용
  - 커밋: b8103ee

- [x] **5. gates.py에 SEO 검사 항목 추가**
  - SEO구조 게이트: H2 2개 이상 + JSON-LD 존재
  - 커밋: f972e98

- [x] **6. Google Analytics 4 연동 (선택)**
  - SETUP.md에 GA4 연동 가이드 추가
  - 커밋: 6456af2

---

## 진행 로그

- 1번 완료: 8150c18 (템플릿 SEO 태그 블록)
- 2번 완료: 4207d11 (CURATE_PROMPT SEO 지시)
- 3번 완료: 6d622db (publish.py _inject_seo)
- 4번 완료: b8103ee (기존 글 SEO 태그 소급)
- 5번 완료: f972e98 (gates.py SEO구조 게이트)
- 6번 완료: 6456af2 (SETUP.md GA4 가이드)
- SEO 최적화 전체 완료
