#!/usr/bin/env python3
"""Blogger OAuth 최초 인증 스크립트 (1회만 실행).

실행 후 나오는 URL을 브라우저에서 열고 구글 계정 동의를 완료하면
이 폴더에 token.json이 생성된다. 이후 publish.py가 이 토큰을 사용한다.
"""

import sys
import webbrowser
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/blogger"]
HERE = Path(__file__).resolve().parent
CLIENT_SECRET = HERE / "client_secret.json"
TOKEN = HERE / "token.json"
PORT = 8080


def main() -> None:
    if not CLIENT_SECRET.exists():
        sys.exit(f"client_secret.json 없음: {CLIENT_SECRET}")

    print("OAuth 인증을 시작합니다...", flush=True)
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)

    creds = flow.run_local_server(
        port=PORT,
        open_browser=False,
        success_message="인증 완료. 이 창을 닫아도 됩니다.",
    )

    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    print(f"\n인증 완료. 토큰 저장: {TOKEN}", flush=True)

    auth_url = f"http://localhost:{PORT}"
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    from googleapiclient.discovery import build

    service = build("blogger", "v3", credentials=creds)
    blogs = service.blogs().listByUser(userId="self").execute()
    print("\n연결된 블로그:", flush=True)
    for b in blogs.get("items", []):
        print(f"  - 이름: {b['name']}", flush=True)
        print(f"    URL : {b['url']}", flush=True)
        print(f"    ID  : {b['id']}", flush=True)


if __name__ == "__main__":
    main()
