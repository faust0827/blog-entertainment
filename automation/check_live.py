#!/usr/bin/env python3
"""sitemap.xml vs index_urls.txt 대조 + LIVE 200/404/redirect 전수 점검.
사용: .venv/bin/python automation/check_live.py [--sitemap url] [--index index_urls.txt] [--out data/live_check.json]
"""
import argparse, json, re, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/126 Safari/537.36"}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def fetch(url, follow=True):
    req = urllib.request.Request(url, headers=UA)
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(req, timeout=30)
        body = r.read().decode("utf-8", "ignore")
        return r.status, r.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, url, e.read().decode("utf-8", "ignore") if e.fp else ""
    except Exception as e:
        return None, url, f"ERR: {e}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitemap", default="https://issuedayissue.blogspot.com/sitemap.xml")
    ap.add_argument("--index", default=str(ROOT / "index_urls.txt"))
    ap.add_argument("--out", default=str(ROOT / "data" / "live_check.json"))
    a = ap.parse_args()

    status, _, sm = fetch(a.sitemap)
    if status != 200:
        print(f"sitemap fetch fail: {status}", file=sys.stderr); return 1
    sitemap = sorted(set(re.findall(r"<loc>([^<]+)</loc>", sm)))
    index = sorted({l.strip() for l in Path(a.index).read_text().splitlines() if l.strip() and not l.startswith("#")})

    only_sitemap = sorted(set(sitemap) - set(index))
    only_index = sorted(set(index) - set(sitemap))

    results = []
    for url in sitemap:
        code, final, body = fetch(url, follow=False)
        loc = ""
        m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', body)
        if not m:
            m = re.search(r'href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', body)
        if m: loc = m.group(1)
        t = re.search(r"<title>([^<]*)</title>", body)
        results.append({"url": url, "status": code, "final_url": final, "canonical": loc, "title": t.group(1).strip() if t else ""})
        print(f"{code} {url}")

    live = [r for r in results if r["status"] == 200]
    dead = [r for r in results if r["status"] not in (200, 301, 302, 303, 307, 308)]
    redirects = [r for r in results if r["status"] in (301, 302, 303, 307, 308)]

    # url_map 역매핑으로 로컬 파일 분류
    url_map = {}
    ump = ROOT / "automation" / "url_map.json"
    if ump.exists():
        inv = {v: k for k, v in json.loads(ump.read_text()).items()}
    else:
        inv = {}

    def local_title(url):
        fn = inv.get(url)
        if fn and (ROOT / "posts" / fn).exists():
            html = (ROOT / "posts" / fn).read_text(encoding="utf-8", errors="ignore")
            t = re.search(r"<title>([^<]*)</title>", html)
            return fn, (t.group(1).strip() if t else "")
        return fn or "", ""

    for r in results:
        fn, lt = local_title(r["url"])
        r["local_file"] = fn; r["local_title"] = lt
        r["is_guide"] = bool(re.search(r"guide|comparison|calculator|free-", fn or ""))

    guides = [r for r in results if r["is_guide"]]
    community = [r for r in results if not r["is_guide"]]

    out = {"sitemap_count": len(sitemap), "index_count": len(index),
           "only_in_sitemap": only_sitemap, "only_in_index": only_index,
           "live_200": len(live), "dead": dead, "redirects": redirects,
           "guide_live": len(guides), "community_live": len(community),
           "results": results}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\nsummary: sitemap={len(sitemap)} index={len(index)} live200={len(live)} dead={len(dead)} redirect={len(redirects)} guide={len(guides)} community={len(community)}")
    print(f"only_sitemap={only_sitemap} only_index={only_index}")
    print(f"wrote {a.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
