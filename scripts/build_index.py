#!/usr/bin/env python3
"""Build and check POSTS.md, the mapping between thoughts/*.md and GitHub issues.

Default: regenerate POSTS.md.
--check: report local files whose body changed since POSTS.md was generated,
plus files added or removed. Exit code is non-zero when anything changed.
"""

import argparse
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THOUGHTS = os.path.join(ROOT, "thoughts")
INDEX = os.path.join(ROOT, "POSTS.md")
REPO_URL = "https://github.com/QingyaFan/blog/issues"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
STATE_RE = re.compile(r"<!-- index-state\s*(\{.*?\})\s*-->", re.S)


def parse_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not key:
            continue
        if key in ("issue", "labels", "images"):
            if value.startswith(("{", "[")):
                try:
                    meta[key] = json.loads(value)
                except json.JSONDecodeError:
                    meta[key] = value
            else:
                try:
                    meta[key] = int(value)
                except ValueError:
                    meta[key] = value
        elif value.startswith('"'):
            try:
                meta[key] = json.loads(value)
            except json.JSONDecodeError:
                meta[key] = value
        else:
            meta[key] = value
    return meta, text[m.end():]


def first_heading(body):
    stripped = body.lstrip("\n")
    first, _, _ = stripped.partition("\n")
    if first.startswith("# ") and not first.startswith("## "):
        return first[2:].strip()
    return None


def digest(body):
    return hashlib.sha256(body.strip().encode("utf-8")).hexdigest()[:8]


def load_posts():
    posts = []
    for name in sorted(os.listdir(THOUGHTS)):
        if not name.endswith(".md") or name == "INDEX.md":
            continue
        path = os.path.join(THOUGHTS, name)
        text = open(path, encoding="utf-8").read()
        meta, body = parse_front_matter(text)
        title = first_heading(body) or meta.get("title") or os.path.splitext(name)[0]
        posts.append(
            {
                "name": name,
                "title": str(title),
                "issue": meta.get("issue") if isinstance(meta.get("issue"), int) else None,
                "state": meta.get("state") or "draft",
                "updated": meta.get("updated") or "",
                "hash": digest(body),
            }
        )
    return posts


def md_link(name):
    return f"[{name}](<thoughts/{name}>)".replace("|", "\\|")


def render(posts):
    published = sorted(
        (p for p in posts if p["issue"]), key=lambda p: p["issue"]
    )
    drafts = sorted((p for p in posts if not p["issue"]), key=lambda p: p["name"])

    lines = [
        "# 文章索引",
        "",
        "`thoughts/` 中的 Markdown 与 GitHub issue 的对应关系，由 "
        "`scripts/build_index.py` 生成。本地 `thoughts/` 是写作副本，GitHub issue 是发布副本；"
        "修改文章后，同步到对应 issue 前先确认，不要直接编辑 issue。",
        "",
        f"- 已发布：{len(published)} 篇",
        f"- 草稿：{len(drafts)} 篇",
        "",
        "## 已发布",
        "",
        "| 本地文件 | Issue | 标题 | 状态 | Issue 更新 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for post in published:
        title = post["title"].replace("|", "\\|")
        lines.append(
            f"| {md_link(post['name'])} | [#{post['issue']}]({REPO_URL}/{post['issue']}) "
            f"| {title} | {post['state']} | {post['updated']} |"
        )

    lines += ["", "## 草稿", ""]
    if drafts:
        lines += ["| 本地文件 | 标题 |", "| --- | --- |"]
        for post in drafts:
            lines.append(f"| {md_link(post['name'])} | {post['title'].replace('|', '\\|')} |")
    else:
        lines.append("（无）")

    state = {p["name"]: p["hash"] for p in posts}
    lines += [
        "",
        "<!-- index-state",
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True),
        "-->",
        "",
    ]
    return "\n".join(lines)


def check(posts):
    if not os.path.exists(INDEX):
        print(f"{INDEX} not found; run build_index.py first")
        return 1
    text = open(INDEX, encoding="utf-8").read()
    m = STATE_RE.search(text)
    if not m:
        print("index state block not found; regenerate POSTS.md")
        return 1
    recorded = json.loads(m.group(1))
    current = {p["name"]: p for p in posts}

    changed = [n for n, p in current.items() if n in recorded and recorded[n] != p["hash"]]
    added = [n for n in current if n not in recorded]
    removed = [n for n in recorded if n not in current]

    for name in changed:
        post = current[name]
        issue = f"issue #{post['issue']}" if post["issue"] else "draft"
        print(f"changed: thoughts/{name} ({issue})")
    for name in added:
        post = current[name]
        issue = f"issue #{post['issue']}" if post["issue"] else "draft"
        print(f"new:     thoughts/{name} ({issue})")
    for name in removed:
        print(f"missing: thoughts/{name}")

    if not changed and not added and not removed:
        print("no local changes")
        return 0
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report local changes without rewriting")
    args = parser.parse_args()

    posts = load_posts()
    if args.check:
        return check(posts)
    with open(INDEX, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(posts))
    print(f"wrote {INDEX}: {len(posts)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())