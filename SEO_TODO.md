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
  - parse_html에서 title/description 추출 → JSON-LD + OG + Canonical 자동 삽입
  - 커밋: 6d622db

- [x] **4. 기존 글(posts/)에 SEO 태그 소급 적용**
  - 4개 기존 글에 SEO 태그 추가
  - 커밋: 6d622db

- [x] **5. gates.py에 SEO 검사 항목 추가**
  - 메타 description 키워드, H2 최소 2개, JSON-LD 존재 여부
  - 커밋: b8103ee

- [ ] **6. Google Analytics 4 연동 (선택)**
  - Blogger 테마에 GA4 스크립트 추가 가이드
  - 커밋: f972e98

---

## 진행 로그

_(각 항목 완료 시 여기에 기록)_
