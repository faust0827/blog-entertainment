#!/usr/bin/env bash
set -u
PROJECT=/home/j/문서/project/blog-entertainment
cd "$PROJECT"
echo "=== crawler ==="
timeout 300 .venv/bin/python automation/crawler.py || true
echo "=== curate ==="
.venv/bin/python automation/curate.py
echo "=== publish new drafts ==="
find posts -maxdepth 1 -name '*.html' -newer .pipeline_marker -print0 | while IFS= read -r -d '' f; do
  if .venv/bin/python automation/publish.py "$f" --check-only >/tmp/blog_gate.log 2>&1; then
    if .venv/bin/python automation/publish.py "$f" >/tmp/blog_pub.log 2>&1; then
      echo "PUBLISHED_DRAFT: $f"
    else
      echo "PUBLISH_FAILED: $f"; cat /tmp/blog_pub.log
    fi
  else
    echo "GATE_FAILED: $f"; cat /tmp/blog_gate.log
  fi
done
touch .pipeline_marker
echo "=== done ==="
