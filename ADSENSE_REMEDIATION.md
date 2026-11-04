# AdSense 대응책 (IssueIssue 블로그)

`issuedayissue_adsense_strategy.md` 진단에 따른 실행 대응책. 코드·콘텐츠·운영 조치를 우선순위별로 정리.

## 1. 코드 레벨 조치 (완료)

- `automation/filter.py`
  - 욕설·비속어(`PROFANITY_KEYWORDS`), 인터넷 은어(`RAW_SLANG_TOKENS`) 필터 추가
  - `MAX_DAILY` 3 → 2 (발행 속도 제한)
- `automation/gates.py`
  - 게이트 3종 추가: `비속어`, `댓글은어`, `닉네임` (총 10종)
  - 모든 `posts/*.html` 10/10 통과 확인
- `automation/curate.py`, `templates/post-template.md`
  - 비속어/은어/닉네임/개인 사연·의료 정보 직접 인용 금지 규칙 추가
  - 글마다 구조 반복 금지 규칙 추가
- 기존 글 16개에서 비속어·은어·닉네임 직접 노출 제거 (중립 요약으로 대체)

## 2. 콘텐츠 방향 (확정)

- 주력 축: "디지털 생활 연구소 + AI 실험실 + 지식 사전"
- 글 유형: 문제 해결형 가이드, 비교표/계산기, 공공데이터 해설, AI 도구 실험, 기술 상식 검증
- 차별화 요소: 글마다 비교표, 계산 사례, 단계별 안내, 공식 출처, 실패 사례, 선택 기준 중 2~3개 포함
- 건강·의료·투자 조언, 커뮤니티 댓글/개인 사연 옮기기, 가짜 경험담은 금지
- 개인정보·신체 사진이 포함된 글은 비공개 처리 (완료: 피지낭종, 쉬었음 청년, 이태원 참사)

## 3. Blogger 수동 조치 (필수)

- [ ] 메뉴에 소개/문의/개인정보처리방침/이용약관 페이지 링크 추가
- [ ] 각 글의 "검색 설명(Search Description)" 입력 (현재 HTML meta는 Blogger에서 무시됨)
- [ ] 라벨(카테고리) 정리: 사회이슈 / 인터넷트렌드 / 생활정보
- [ ] robots.txt sitemap을 `issuedayissue.blogspot.com`으로 수정
- [ ] Google Search Console 등록 및 색인 확인
- [ ] ads.txt / AdSense 연결 및 사이트 소유권 확인
- [ ] 발행 속도: 하루 1건, 예약 발행 사용 (현재 5개 예약: 11/3~11/7)

## 4. 운영 우선순위

1. 오늘의 지원금 블로그를 먼저 AdSense 통과 (이 블로그는 방향 전환 후 별도 신청)
2. IssueIssue 기존 글 분류: 댓글 요약 위주 글은 비공개/재작성 (완료: 고위험 3개 삭제)
3. 디지털 생활·AI 활용·지식 사전 글을 하루 1건씩 축적 (계산기·비교표·문제 해결 가이드 우선)
4. 두 블로그에 동일 계정 사용 시 한쪽 정책 문제가 전체 심사에 영향 — IssueIssue는 현재 상태로 신청 금지

## 5. 검증 명령

```bash
cd /home/j/문서/project/blog-entertainment
for f in posts/*.html; do python3 automation/gates.py "$f"; done
.venv/bin/python automation/filter.py
```
