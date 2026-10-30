#!/usr/bin/env python3
"""Blogger 글 발행 스크립트 (커뮤니티 큐레이션 블로그용).

사용법:
  python automation/publish.py posts/sample.html --check-only          # 게이트 점검만
  python automation/publish.py posts/sample.html                       # 초안(draft) 발행
  python automation/publish.py posts/sample.html --publish --reviewed  # 검수 후 공개
  python automation/publish.py posts/x.html --update POST_ID --reviewed
  python automation/publish.py posts/slug.html --schedule 2026-11-07T10:30:00+09:00 --labels 연예이슈
  python automation/publish.py posts/*.html --draft

HTML 문서에서는 <body> 안의 콘텐츠만 발행한다. <title>은 제목으로 사용하고,
description 메타는 수동 입력 안내에 사용한다.

종료 코드: 0 성공 · 1 파일/API 오류 · 2 인자 오류 · 3 게이트 미통과
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

try:
    from automation import gates
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gates

SCOPES = ["https://www.googleapis.com/auth/blogger"]
HERE = Path(__file__).resolve().parent
CLIENT_SECRET = HERE / "client_secret.json"
TOKEN = HERE / "token.json"
LEDGER = HERE / "schedule_ledger.json"
URL_MAP = HERE / "url_map.json"
KST = timezone(timedelta(hours=9))

DEFAULT_BLOG_URL = "issuedayissue.blogspot.com"


def load_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
    if not creds or not creds.valid:
        print("토큰이 유효하지 않습니다. auth_setup.py를 먼저 실행하세요.")
        sys.exit(1)
    return creds


def get_blog_id(service) -> str:
    blogs = service.blogs().listByUser(userId="self").execute()
    items = blogs.get("items", [])
    if not items:
        sys.exit("연결된 블로그가 없습니다.")
    if len(items) == 1:
        return items[0]["id"]
    for b in items:
        if DEFAULT_BLOG_URL in b.get("url", ""):
            print(f"블로그 자동 선택: {b['name']} ({b['url']})")
            return b["id"]
    print("여러 블로그가 있습니다. --blog-id를 지정하세요:")
    for b in items:
        print(f"  {b['id']}  {b['name']}  {b['url']}")
    sys.exit(1)


# ---------- ledger ----------

def load_url_map(path: Path | None = None) -> dict:
    path = path or URL_MAP
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_url_map(url_map: dict, path: Path | None = None) -> None:
    path = path or URL_MAP
    path.write_text(json.dumps(url_map, ensure_ascii=False, indent=2), encoding="utf-8")


def _strip_related(content: str) -> str:
    """기존 '관련 글' 섹션 제거 (중복/구버전 제거)."""
    import re as _re
    content = _re.sub(r"\\n*<h2>관련 글</h2>\\n*<ul>.*?</ul>\\n*", "\\n", content, flags=_re.S)
    return content.rstrip()


def _inject_related(content: str, current_name: str, url_map: dict) -> str:
    """기존 관련 글 섹션을 제거하고, url_map 기반으로 새 관련 글 섹션을 삽입."""
    content = _strip_related(content)
    if not url_map:
        return content
    current_words = set(current_name.lower().replace("-", " ").replace("_", " ").split())
    # also use content words
    import re as _re
    content_words = set(_re.findall(r"[가-힣A-Za-z0-9]+", content.lower()))
    candidates = []
    for name, u in url_map.items():
        if name == current_name or not u:
            continue
        # title: prefer <title> from local file
        title = name.replace("-", " ").replace("_", " ").replace(".html", "")
        local = HERE.parent / "posts" / name
        if local.exists():
            try:
                import re as _re2
                m = _re2.search(r"<title>(.*?)</title>", local.read_text(encoding="utf-8"), _re2.S)
                if m:
                    title = m.group(1).strip()
            except OSError:
                pass
        name_words = set(name.lower().replace("-", " ").replace("_", " ").split())
        # also content words of candidate post title
        title_words = set(_re.findall(r"[가-힣A-Za-z0-9]+", title.lower()))
        overlap = len((current_words | content_words) & (name_words | title_words))
        if overlap >= 1:
            candidates.append((overlap, title, u))
    candidates.sort(reverse=True)
    picks = candidates[:3]
    if not picks:
        return content
    items = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{t}</a></li>' for _, t, u in picks)
    return content.rstrip() + "\\n\\n<h2>관련 글</h2>\\n<ul>\\n" + items + "\\n</ul>\\n"


def load_ledger(path: Path | None = None) -> list[dict]:
    path = path or LEDGER
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    entries = data.get("entries", [])
    return entries if isinstance(entries, list) else []


def save_ledger(entries: list[dict], path: Path | None = None) -> None:
    path = path or LEDGER
    path.write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")


def count_scheduled_on(ledger: list[dict], date_iso: str, *, exclude_post_id: str | None = None) -> int:
    count = 0
    for entry in ledger:
        if exclude_post_id is not None and str(entry.get("post_id", "")) == str(exclude_post_id):
            continue
        try:
            day = datetime.fromisoformat(entry["publish_date"]).astimezone(KST).date().isoformat()
        except (KeyError, TypeError, ValueError):
            continue
        if day == date_iso:
            count += 1
    return count


def schedule_post(service, blog_id: str, post_id: str, publish_date: str, ledger_path: Path | None = None):
    ledger_path = ledger_path or LEDGER
    post = service.posts().publish(blogId=blog_id, postId=post_id, publishDate=publish_date).execute()
    if post.get("status") != "SCHEDULED":
        raise RuntimeError(f"예약 상태 확인 실패: 예상 SCHEDULED, 실제 {post.get('status', '?')}")
    ledger = load_ledger(ledger_path)
    scheduled_post_id = str(post.get("id", post_id))
    ledger = [e for e in ledger if str(e.get("post_id", "")) != scheduled_post_id]
    ledger.append({
        "post_id": scheduled_post_id,
        "title": post.get("title", ""),
        "publish_date": publish_date,
        "scheduled_at": datetime.now(KST).isoformat(timespec="seconds"),
    })
    save_ledger(ledger, ledger_path)
    print(f"[예약] {post.get('title', '')}")
    print(f"  발행 예정: {publish_date}")
    print(f"  ID : {post.get('id', post_id)}")
    return post


# ---------- HTML parsing ----------

class _BloggerContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.body_parts: list[str] = []
        self.in_body = False
        self.found_body = False
        self.in_title = False
        self.title_parts: list[str] = []
        self.description: str | None = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "body":
            self.found_body = True
            self.in_body = True
        elif tag == "meta" and attributes.get("name", "").lower() == "description":
            self.description = attributes.get("content")
        elif tag == "title":
            self.in_title = True
        elif self.in_body:
            self.body_parts.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if self.in_body and tag != "body":
            self.body_parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False
        elif tag == "title":
            self.in_title = False
        elif self.in_body:
            self.body_parts.append(f"</{tag}>")

    def handle_data(self, data):
        if self.in_body:
            self.body_parts.append(data)
        if self.in_title:
            self.title_parts.append(data)

    def handle_entityref(self, name):
        token = f"&{name};"
        if self.in_body:
            self.body_parts.append(token)
        if self.in_title:
            self.title_parts.append(token)

    def handle_charref(self, name):
        token = f"&#{name};"
        if self.in_body:
            self.body_parts.append(token)
        if self.in_title:
            self.title_parts.append(token)

    def handle_comment(self, data):
        if self.in_body:
            self.body_parts.append(f"<!--{data}-->")


def parse_html(html: str, fallback_title: str):
    from html import unescape

    parser = _BloggerContentParser()
    parser.feed(html)
    parser.close()
    content = "".join(parser.body_parts).strip() if parser.found_body else html.strip()
    title = " ".join("".join(parser.title_parts).split()) or fallback_title
    description = parser.description.strip() if parser.description else None
    return content, title, description


def print_search_description(description):
    if description:
        print(f"  검색 설명(글 설정에 수동 입력): {description}")


# ---------- publish helpers ----------

def _inject_seo(content: str, title: str, description: str | None) -> str:
    """본문에 JSON-LD 구조화 데이터(Article)를 삽입 (SEO). 이미 있으면 건너뜀."""
    if "application/ld+json" in content:
        return content
    from datetime import date
    import json as _json
    payload = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "datePublished": date.today().isoformat(),
        "author": {"@type": "Organization", "name": "커뮤니티 큐레이션 블로그"},
        "publisher": {"@type": "Organization", "name": "커뮤니티 큐레이션 블로그"},
    }
    if description:
        payload["description"] = description
    script = '<script type="application/ld+json">' + _json.dumps(payload, ensure_ascii=False) + "</script>"
    return content.rstrip() + "\n" + script


def publish_one(service, blog_id, path, html, *, draft, title=None, labels=None):
    content, extracted_title, description = parse_html(html, path.stem)
    final_title = title or extracted_title
    content = _inject_seo(content, final_title, description)
    # 내부 링크 자동 삽입 (기존 관련 글 섹션 제거 후 재삽입)
    url_map = load_url_map()
    content = _inject_related(content, path.name, url_map)
    body = {"kind": "blogger#post", "title": final_title, "content": content}
    if labels:
        body["labels"] = labels
    post = service.posts().insert(blogId=blog_id, body=body, isDraft=draft).execute()
    # url_map 갱신
    if post.get("url"):
        url_map[path.name] = post["url"]
        save_url_map(url_map)
    expected = "DRAFT" if draft else "LIVE"
    if post.get("status") != expected:
        raise RuntimeError(f"발행 상태 확인 실패: 예상 {expected}, 실제 {post.get('status', '?')}")
    state = "초안" if post.get("status") == "DRAFT" else post.get("status", "?")
    print(f"[{state}] {post['title']}")
    print(f"  URL: {post.get('url', '(초안이라 공개 URL 없음)')}")
    print(f"  ID : {post['id']}")
    print_search_description(description)
    return post


def update_one(service, blog_id, path, html, post_id, *, title=None, labels=None, publish=False):
    content, extracted_title, description = parse_html(html, path.stem)
    final_title = title or extracted_title
    content = _inject_seo(content, final_title, description)
    url_map = load_url_map()
    content = _inject_related(content, path.name, url_map)
    body = {"kind": "blogger#post", "title": final_title, "content": content}
    if labels:
        body["labels"] = labels
    post = service.posts().update(blogId=blog_id, postId=post_id, body=body, publish=False).execute()
    if post.get("url"):
        url_map[path.name] = post["url"]
        save_url_map(url_map)
    if publish:
        post = service.posts().publish(blogId=blog_id, postId=post_id).execute()
    state = "초안" if post.get("status") == "DRAFT" else post.get("status", "?")
    action = "갱신/공개" if publish else "갱신"
    print(f"[{action}/{state}] {post['title']}")
    if post.get("url"):
        print(f"  URL: {post['url']}")
    print(f"  ID : {post['id']}")
    if publish and post.get("status") != "LIVE":
        raise RuntimeError(f"공개 전환 실패: 예상 LIVE, 실제 {post.get('status', '?')}")
    print_search_description(description)
    return post


def publish_page(service, blog_id, path, html, *, title=None):
    content, extracted_title, description = parse_html(html, path.stem)
    final_title = title or extracted_title
    content = _inject_seo(content, final_title, description)
    body = {"kind": "blogger#page", "title": final_title, "content": content}
    page = service.pages().insert(blogId=blog_id, body=body, isDraft=False).execute()
    print(f"[페이지] {page['title']}")
    print(f"  URL: {page.get('url', '?')}")
    print(f"  ID : {page['id']}")
    print_search_description(description)
    return page


def run_gate_for_file(path, html):
    results = gates.run_gates(html)
    print(gates.format_results(results, str(path)))
    return bool(gates.failed(results))


def main() -> int:
    parser = argparse.ArgumentParser(description="Blogger 글 발행")
    parser.add_argument("files", nargs="+", type=Path, help="발행할 HTML 파일")
    parser.add_argument("--publish", action="store_true", help="공개 발행 (기본은 초안)")
    parser.add_argument("--draft", action="store_true", help="초안으로 저장 (기본값)")
    parser.add_argument("--reviewed", action="store_true", help="검수 완료 확인")
    parser.add_argument("--title", help="제목 지정")
    parser.add_argument("--labels", help="라벨(쉼표 구분)")
    parser.add_argument("--blog-id", help="블로그 ID 지정")
    parser.add_argument("--page", action="store_true", help="페이지로 발행")
    parser.add_argument("--update", metavar="POST_ID", help="기존 글 갱신")
    parser.add_argument("--gates", action="store_true", help="품질 게이트 실행")
    parser.add_argument("--check-only", action="store_true", help="게이트 점검만")
    parser.add_argument("--schedule", metavar="RFC3339", help="예약 발행 (예: 2026-11-07T10:30:00+09:00)")
    args = parser.parse_args()

    if args.publish and args.draft:
        parser.error("--publish와 --draft는 함께 사용할 수 없습니다")
    if args.page and args.update:
        parser.error("--update은 글에만 사용할 수 있습니다")
    if args.schedule and args.publish:
        parser.error("--schedule과 --publish는 함께 사용할 수 없습니다")

    schedule_date = None
    if args.schedule:
        try:
            schedule_dt = datetime.fromisoformat(args.schedule)
        except ValueError:
            parser.error("--schedule은 RFC3339 형식이어야 합니다")
        if schedule_dt.tzinfo is None:
            parser.error("--schedule에는 시간대(+09:00 등)가 필요합니다")
        schedule_date = schedule_dt.astimezone(KST).date().isoformat()

    needs_reviewed = (args.publish or args.page or (args.update and not args.schedule))
    if needs_reviewed and not args.reviewed:
        parser.error("즉시 공개 발행·페이지 발행·기존 글 즉시 공개에는 --reviewed가 필요합니다")

    missing = [p for p in args.files if not p.is_file()]
    if missing:
        for p in missing:
            print(f"파일 없음: {p}", file=sys.stderr)
        return 1

    contents = []
    for p in args.files:
        try:
            contents.append((p, p.read_text(encoding="utf-8")))
        except (OSError, UnicodeError) as e:
            print(f"파일 읽기 실패: {p} — {e}", file=sys.stderr)
            return 1

    strict = args.publish or args.page or args.gates or args.check_only or bool(args.schedule)
    gate_blocked = []
    if strict:
        for path, html in contents:
            if run_gate_for_file(path, html):
                gate_blocked.append(path)
        if gate_blocked:
            print(f"게이트 미통과: {len(gate_blocked)}개", file=sys.stderr)
            return 3
        if args.check_only:
            return 0

    creds = load_credentials()
    from googleapiclient.discovery import build
    service = build("blogger", "v3", credentials=creds)
    blog_id = args.blog_id or get_blog_id(service)
    labels = [l.strip() for l in args.labels.split(",") if l.strip()] if args.labels else None

    failures = []
    for path, html in contents:
        try:
            if args.page:
                publish_page(service, blog_id, path, html, title=args.title)
            elif args.update:
                update_one(service, blog_id, path, html, args.update, title=args.title, labels=labels, publish=args.publish)
                if args.schedule:
                    schedule_post(service, blog_id, args.update, args.schedule)
            elif args.schedule:
                post = publish_one(service, blog_id, path, html, draft=True, title=args.title, labels=labels)
                schedule_post(service, blog_id, post["id"], args.schedule)
            else:
                publish_one(service, blog_id, path, html, draft=not args.publish, title=args.title, labels=labels)
        except Exception as e:
            print(f"발행 실패: {path} — {e}", file=sys.stderr)
            failures.append(path)

    if failures:
        print(f"실패: {len(failures)}/{len(contents)}개", file=sys.stderr)
        return 1
    print("\\n색인 요청: .venv/bin/python automation/submit_index.py <발행된 URL>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
