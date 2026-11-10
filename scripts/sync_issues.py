#!/usr/bin/env python3
"""Sync GitHub issues of the blog repo into thoughts/*.md and images/.

Default mode is non-destructive: it only creates Markdown for issues that do
not exist locally yet, and never touches existing files. Use --force to
regenerate every file from GitHub (local edits will be lost).
"""

import argparse
import concurrent.futures
import glob
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

REPO = "QingyaFan/blog"
API = f"https://api.github.com/repos/{REPO}/issues?state=all&per_page=100&page={{}}"
UA = "blog-issue-sync/1.0 (+https://github.com/QingyaFan/blog)"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THOUGHTS = os.path.join(ROOT, "thoughts")
IMAGES = os.path.join(ROOT, "images")

MD_IMG = r'!\[[^\]]*\]\((https?://[^)\s]+)\)'
HTML_IMG = r'<img\b[^>]*\bsrc\s*=\s*"([^"]+)"'
IMG_RE = re.compile(MD_IMG + "|" + HTML_IMG, re.I)
INVALID_FS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

EXT_BY_TYPE = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "image/bmp": "bmp",
    "image/avif": "avif",
}


def fetch_json(url):
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last = None
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except Exception as exc:  # noqa: BLE001
            last = exc
    raise RuntimeError(f"GitHub API failed: {url}: {last}")


def fetch_issues():
    issues, page = [], 1
    while True:
        batch = fetch_json(API.format(page))
        issues.extend(batch)
        print(f"api page {page}: {len(batch)} issues", flush=True)
        if len(batch) < 100:
            break
        page += 1
    return [i for i in issues if "pull_request" not in i]


def sanitize(title, number):
    name = INVALID_FS.sub("-", title)
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip(".-")
    name = name[:70].strip(".-")
    return f"{number:04d}-{name or 'issue'}"


def markdown_path(issue):
    return os.path.join(THOUGHTS, sanitize(issue["title"], issue["number"]) + ".md")


def image_urls(body):
    urls = []
    for m in IMG_RE.finditer(body):
        url = m.group(1) or m.group(2)
        if url not in urls:
            urls.append(url)
    return urls


def raw_url(url):
    p = urllib.parse.urlparse(url)
    if p.netloc == "github.com":
        parts = p.path.split("/")
        if len(parts) >= 6 and parts[3] == "blob":
            return "https://raw.githubusercontent.com/" + "/".join(
                [parts[1], parts[2], parts[4]] + parts[5:]
            )
    return url


def sniff_ext(data, content_type):
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data.startswith(b"BM"):
        return "bmp"
    if b"ftypavif" in data[:32]:
        return "avif"
    head = data[:512].lstrip().lower()
    if head.startswith(b"<svg") or (head.startswith(b"<?xml") and b"<svg" in head):
        return "svg"
    return EXT_BY_TYPE.get(content_type)


def download_image(url):
    target = raw_url(url)
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "image/*,*/*;q=0.8"}
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(target, headers=headers), timeout=90
            ) as resp:
                data = resp.read()
                content_type = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            ext = sniff_ext(data, content_type)
            if not ext:
                raise ValueError(f"not an image (content-type={content_type}, {len(data)} bytes)")
            if len(data) < 128:
                raise ValueError(f"suspiciously small image ({len(data)} bytes)")
            return data, ext
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 * (attempt + 1))
    raise last


def plan_images(issues):
    """Map url -> (issue number, seq, digest) for the given issues."""
    plan = {}
    for issue in issues:
        body = issue.get("body") or ""
        seq = 0
        for url in image_urls(body):
            if url in plan:
                continue
            seq += 1
            digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
            plan[url] = (issue["number"], seq, digest)
    return plan


def resolve_images(plan):
    os.makedirs(IMAGES, exist_ok=True)
    results, failures = {}, {}

    def work(item):
        url, (number, seq, digest) = item
        prefix = os.path.join(IMAGES, f"issue-{number:04d}-{seq:02d}-{digest}")
        existing = glob.glob(prefix + ".*")
        if existing:
            return url, os.path.basename(existing[0])
        data, ext = download_image(url)
        path = f"{prefix}.{ext}"
        with open(path, "wb") as fh:
            fh.write(data)
        return url, os.path.basename(path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(work, item): item for item in plan.items()}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future][0]
            try:
                key, name = future.result()
                results[key] = name
            except Exception as exc:  # noqa: BLE001
                failures[url] = str(exc)
    return results, failures


def render(issue, image_map):
    raw_body = (issue.get("body") or "").replace("\r\n", "\n").replace("\r", "\n")
    image_mapping = {
        image_map[url]: raw_url(url) for url in image_urls(raw_body) if url in image_map
    }
    body = raw_body.strip()
    for url, name in image_map.items():
        body = body.replace(url, f"../images/{name}")

    title = issue["title"].strip()
    labels = [label["name"] for label in issue.get("labels") or []]
    lines = [
        "---",
        f"issue: {issue['number']}",
        f"title: {json.dumps(title, ensure_ascii=False)}",
        f"state: {issue['state']}",
        f"created: {issue['created_at'][:10]}",
        f"updated: {issue['updated_at'][:10]}",
        f"url: {issue['html_url']}",
        f"labels: {json.dumps(labels, ensure_ascii=False)}",
    ]
    if image_mapping:
        lines.append(f"images: {json.dumps(image_mapping, ensure_ascii=False)}")
    lines += [
        "---",
        "",
        f"# {title}",
        "",
    ]
    return "\n".join(lines) + (body + "\n" if body else "")


def write_thoughts(issues, image_map, force):
    os.makedirs(THOUGHTS, exist_ok=True)
    if force:
        for name in os.listdir(THOUGHTS):
            if re.fullmatch(r"\d{4}-.*\.md", name):
                os.remove(os.path.join(THOUGHTS, name))

    written, skipped = 0, 0
    for issue in issues:
        path = markdown_path(issue)
        if os.path.exists(path) and not force:
            skipped += 1
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render(issue, image_map))
        written += 1
    return written, skipped


def write_index(issues):
    rows = [
        "| # | 标题 | 状态 | 创建日期 |",
        "| --- | --- | --- | --- |",
    ]
    for issue in issues:
        stem = sanitize(issue["title"], issue["number"])
        safe_title = issue["title"].replace("|", "\\|")
        rows.append(
            f"| {issue['number']} | [{safe_title}]({stem}.md) | {issue['state']} | {issue['created_at'][:10]} |"
        )
    text = (
        "# Issue 归档\n\n"
        f"共 {len(issues)} 篇，按 issue 编号升序。正文由 `scripts/sync_issues.py` 从 "
        "[QingyaFan/blog](https://github.com/QingyaFan/blog/issues) 拉取，插图位于 `../images/`。\n\n"
        + "\n".join(rows)
        + "\n"
    )
    with open(os.path.join(THOUGHTS, "INDEX.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing thoughts/*.md files (local edits will be lost)",
    )
    args = parser.parse_args()

    issues = sorted(fetch_issues(), key=lambda i: i["number"])
    targets = issues if args.force else [i for i in issues if not os.path.exists(markdown_path(i))]
    print(f"issues: {len(issues)}, to create: {len(targets)}", flush=True)

    plan = plan_images(targets)
    print(f"unique images: {len(plan)}", flush=True)
    image_map, failures = resolve_images(plan)

    written, skipped = write_thoughts(issues, image_map, args.force)
    write_index(issues)

    print(f"created: {written}, skipped existing: {skipped}", flush=True)
    print(f"images saved: {len(image_map)}", flush=True)
    if failures:
        print(f"image failures: {len(failures)}", flush=True)
        for url, err in failures.items():
            print(f"  FAIL {url} -> {err}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())