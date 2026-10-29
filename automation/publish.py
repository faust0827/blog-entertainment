#!/usr/bin/env python3
"""Blogger 글 발행 스크립트 (커뮤니티 큐레이션 블로그용).

사용법:
  python3 publish.py posts/sample.html --check-only
  python3 publish.py posts/sample.html --draft
  python3 publish.py posts/sample.html --publish --reviewed
"""

import argparse
import os
import sys
from html.parser import HTMLParser
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gates

SCOPES = ["https://www.googleapis.com/auth/blogger"]
HERE = Path(__file__).resolve().parent
CLIENT_SECRET = HERE / "client_secret.json"
TOKEN = HERE / "token.json"
LEDGER = HERE / "schedule_ledger.json"
DEFAULT_BLOG_URL = "issuedayissue.blogspot.com"

AD_SNIPPET = (
    '<div style="text-align:center;margin:16px 0;">'
    '<script src="https://ads-partners.coupang.com/g.js"></script>'
    '<script>new PartnersCoupang.G({"id":1044539,"template":"carousel","trackingCode":"AF3610050","width":"300","height":"250","tsource":""});</script>'
    "</div>"
)


def load_credentials():
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


def get_blog_id(service, preferred: str = "") -> str:
    blogs = service.blogs().listByUser(userId="self").execute()
    items = blogs.get("items", []) or blogs.get("blogs", [])
    if not items:
        sys.exit("연결된 블로그가 없습니다.")
    if len(items) == 1:
        return items[0]["id"]
    if preferred:
        for b in items:
            if preferred in b.get("url", ""):
                print(f"블로그 자동 선택: {b['name']} ({b['url']})")
                return b["id"]
    print("여러 블로그가 있습니다. --blog-id를 지정하세요:")
    for b in items:
        print(f"  {b['id']}  {b['name']}  {b['url']}")
    sys.exit(1)


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


def parse_html(html, fallback_title):
    from html import unescape

    parser = _BloggerContentParser()
    parser.feed(html)
    parser.close()
    content = "".join(parser.body_parts).strip() if parser.found_body else html.strip()
    title = " ".join(parser.title_parts).strip() or fallback_title
    title = " ".join(title.split())
    description = parser.description.strip() if parser.description else None
    return content, unescape(title), description


def print_search_description(description):
    if description:
        print(f"  검색 설명(글 설정에 수동 입력): {description}")


def _add_blank_targets(content: str) -> str:
    def repl(m):
        tag = m.group(0)
        if "target=" in tag:
            return tag
        return tag.replace("<a ", '<a target="_blank" ', 1)
    return re.sub(r"<a\s+[^>]*>", repl, content)


def publish_one(service, blog_id, path, html, *, draft, title, labels):
    content, extracted_title, description = parse_html(html, path.stem)
    content = _add_blank_targets(content)
    if AD_SNIPPET not in content:
        content = content + "\n" + AD_SNIPPET
    body = {"kind": "blogger#post", "title": title or extracted_title, "content": content}
    if labels:
        body["labels"] = labels
    post = service.posts().insert(blogId=blog_id, body=body, isDraft=draft).execute()
    state = "초안" if post.get("status") == "DRAFT" else post.get("status", "?")
    print(f"[{state}] {post['title']}")
    print(f"  URL: {post.get('url', '(초안이라 공개 URL 없음)')}")
    print(f"  ID : {post['id']}")
    print_search_description(description)
    return post


def update_one(service, blog_id, path, html, post_id, *, title, labels, publish=False):
    content, extracted_title, description = parse_html(html, path.stem)
    content = _add_blank_targets(content)
    if AD_SNIPPET not in content:
        content = content + "\n" + AD_SNIPPET
    body = {"kind": "blogger#post", "title": title or extracted_title, "content": content}
    if labels:
        body["labels"] = labels
    post = service.posts().update(blogId=blog_id, postId=post_id, body=body, publish=False).execute()
    if publish:
        post = service.posts().publish(blogId=blog_id, postId=post_id).execute()
    state = "초안" if post.get("status") == "DRAFT" else post.get("status", "?")
    action = "갱신/공개" if publish else "갱신"
    print(f"[{action}/{state}] {post['title']}")
    if post.get("url"):
        print(f"  URL: {post['url']}")
    print(f"  ID : {post['id']}")
    print_search_description(description)
    return post


def publish_page(service, blog_id, path, html, *, title):
    content, extracted_title, description = parse_html(html, path.stem)
    content = _add_blank_targets(content)
    if AD_SNIPPET not in content:
        content = content + "\n" + AD_SNIPPET
    body = {"kind": "blogger#page", "title": title or extracted_title, "content": content}
    page = service.pages().insert(blogId=blog_id, body=body, isDraft=False).execute()
    print(f"[페이지] {page['title']}")
    print(f"  URL: {page.get('url', '?')}")
    print(f"  ID : {page['id']}")
    print_search_description(description)
    return page


def load_ledger():
    if not LEDGER.exists():
        return []
    try:
        data = __import__("json").loads(LEDGER.read_text(encoding="utf-8"))
    except Exception:
        return []
    entries = data.get("entries", [])
    return entries if isinstance(entries, list) else []


def schedule_post(service, blog_id, post_id, publish_date):
    import json
    from datetime import datetime, timezone, timedelta

    post = service.posts().publish(blogId=blog_id, postId=post_id, publishDate=publish_date).execute()
    if post.get("status") != "SCHEDULED":
        raise RuntimeError(f"예약 상태 확인 실패: 예상 SCHEDULED, 실제 {post.get('status', '?')}")
    ledger = load_ledger()
    scheduled_id = str(post.get("id", post_id))
    ledger = [e for e in ledger if str(e.get("post_id", "")) != scheduled_id]
    ledger.append({"post_id": scheduled_id, "title": post.get("title", ""), "publish_date": publish_date,
                   "scheduled_at": datetime.now().isoformat(timespec="seconds")})
    LEDGER.write_text(__import__("json").dumps({"entries": ledger}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[예약] {post.get('title', '')}")
    print(f"  발행 예정: {publish_date}")
    print(f"  ID : {post.get('id', post_id)}")
    return post


def run_gate_stage(path, html):
    results = gates.run_gates(html)
    print(gates.format_results(results, str(path)))
    return bool(gates.failed(results))


def main():
    parser = argparse.ArgumentParser(description="Blogger 글 발행")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--reviewed", action="store_true")
    parser.add_argument("--title")
    parser.add_argument("--labels")
    parser.add_argument("--blog-id")
    parser.add_argument("--page", action="store_true")
    parser.add_argument("--update", metavar="POST_ID")
    parser.add_argument("--gates", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--schedule", metavar="RFC3339")
    parser.add_argument("--auto", action="store_true")
    args = parser.parse_args()

    if args.publish and args.draft:
        parser.error("--publish와 --draft는 함께 사용할 수 없습니다")
    if args.page and args.update:
        parser.error("--update은 글에만 사용할 수 있습니다")
    if args.schedule and args.publish:
        parser.error("--schedule과 --publish는 함께 사용할 수 없습니다")
    schedule_date = None
    if args.schedule:
        from datetime import datetime
        try:
            schedule_dt = datetime.fromisoformat(args.schedule)
        except ValueError:
            parser.error("--schedule은 RFC3339 형식이어야 합니다")
        if schedule_dt.tzinfo is None:
            parser.error("--schedule에는 시간대가 필요합니다")
    auto_enabled = os.environ.get("AUTO_PUBLISH_ENABLED", "").strip() == "1"
    needs_reviewed = (args.publish or args.page or (args.update and not args.schedule)) and not (args.auto and auto_enabled)
    if needs_reviewed and not args.reviewed:
        parser.error("즉시 공개 발행에는 --reviewed가 필요합니다")
    if args.auto and not auto_enabled:
        parser.error("AUTO_PUBLISH_ENABLED=1 필요")
    if args.check_only and (args.publish or args.update or args.reviewed or args.draft or args.schedule):
        parser.error("--check-only는 점검 전용입니다")

    missing = [p for p in args.files if not p.is_file()]
    if missing:
        for p in missing:
            print(f"파일 없음: {p}", file=sys.stderr)
        return 1

    contents = []
    for p in args.files:
        try:
            contents.append((p, p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"파일 읽기 실패: {p} — {e}", file=sys.stderr)
            return 1

    will_live = args.publish or (args.page and not args.check_only)
    will_schedule = bool(args.schedule) and not args.page
    strict = will_live or will_schedule or args.gates or args.check_only

    # check-only: no auth
    if args.check_only:
        blocked = []
        for path, html in contents:
            if run_gate_stage(path, html):
                blocked.append(path)
        if blocked:
            print(f"게이트 미통과: {len(blocked)}개", file=sys.stderr)
            return 3
        return 0

    creds = load_credentials()
    service = build("blogger", "v3", credentials=creds)
    blog_id = args.blog_id or get_blog_id(service, DEFAULT_BLOG_URL or "")
    labels = [x.strip() for x in args.labels.split(",") if x.strip()] if args.labels else None

    failures = []
    blocked = []
    for path, html in contents:
        if strict and run_gate_stage(path, html):
            print(f"게이트 미통과로 발행 보류: {path}", file=sys.stderr)
            blocked.append(path)
            failures.append(path)
            continue
        try:
            if args.page:
                publish_page(service, blog_id, path, html, title=args.title)
            elif args.update:
                update_one(service, blog_id, path, html, args.update, title=args.title, labels=labels, publish=args.publish)
                if will_schedule:
                    schedule_post(service, blog_id, args.update, args.schedule)
            elif will_schedule:
                post = publish_one(service, blog_id, path, html, draft=True, title=args.title, labels=labels)
                schedule_post(service, blog_id, post["id"], args.schedule)
            else:
                publish_one(service, blog_id, path, html, draft=not args.publish, title=args.title, labels=labels)
        except Exception as e:
            print(f"발행 실패: {path} — {e}", file=sys.stderr)
            failures.append(path)

    if failures:
        print(f"실패: {len(failures)}/{len(contents)}개", file=sys.stderr)
        return 3 if blocked else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())