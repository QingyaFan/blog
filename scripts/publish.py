#!/usr/bin/env python3
"""Publish a local thoughts/*.md file as a GitHub issue.

- Front matter `issue: N` present: update issue N.
- No issue number: create a new issue, then write number/url back to front matter.
- Local `../images/<name>` links are published using, in order of preference:
  1. the original URL recorded in front matter `images`;
  2. a raw GitHub URL if the image is tracked in git;
  3. unchanged (with a warning) if the image is untracked.
- Use --dry-run to preview and --force to bypass the remote-update check.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = "QingyaFan/blog"
BRANCH = "master"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PREFIX = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/images/"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
IMG_RE = re.compile(r'(?P<prefix>\]\(|src=")(?P<path>(?:\.\./|\./)?images/[^)\s"]+)')


def gh(args):
    res = subprocess.run(["gh"] + args, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or res.stdout.strip())
    return res.stdout.strip()


def gh_json(args):
    return json.loads(gh(args))


def ensure_auth():
    res = subprocess.run(["gh", "auth", "status"], cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        detail = (res.stderr or res.stdout).strip()
        raise RuntimeError(f"gh is not authenticated. Run `gh auth login`.\n{detail}")


def parse_front_matter(text):
    m = FM_RE.match(text)
    if not m:
        return {}, "", text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not key:
            continue
        if key == "issue":
            try:
                meta[key] = int(value)
            except ValueError:
                meta[key] = value
        elif value.startswith(("{", "[", '"')):
            try:
                meta[key] = json.loads(value)
            except json.JSONDecodeError:
                meta[key] = value
        else:
            meta[key] = value
    return meta, m.group(1), text[m.end():]


def fm_value(key, value):
    if key in ("title", "labels", "images"):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def set_front_matter(text, updates):
    """Update keys in place, preserving unknown fields and the body."""
    m = FM_RE.match(text)
    pending = dict(updates)
    if not m:
        lines = ["---"]
        lines += [f"{k}: {fm_value(k, v)}" for k, v in pending.items()]
        lines.append("---")
        return "\n".join(lines) + "\n\n" + text.lstrip("\n")

    lines = []
    for line in m.group(1).splitlines():
        key = line.split(":", 1)[0].strip() if ":" in line else ""
        if key in pending:
            lines.append(f"{key}: {fm_value(key, pending.pop(key))}")
        else:
            lines.append(line)
    for key, value in pending.items():
        lines.append(f"{key}: {fm_value(key, value)}")
    return "---\n" + "\n".join(lines) + "\n---\n" + text[m.end():]


def split_title(body):
    body = body.lstrip("\n")
    if not body:
        return None, ""
    first, _, rest = body.partition("\n")
    if first.startswith("# ") and not first.startswith("## "):
        return first[2:].strip(), rest.lstrip("\n")
    return None, body


def tracked_images():
    res = subprocess.run(
        ["git", "-C", ROOT, "ls-files", "--", "images"], capture_output=True, text=True
    )
    return set(res.stdout.split())


def rewrite_images(body, image_map, tracked):
    warnings, raw_names = [], []

    def repl(match):
        path = match.group("path")
        name = os.path.basename(path)
        if not os.path.exists(os.path.join(ROOT, "images", name)):
            warnings.append(f"missing local image: {path}")
            return match.group(0)
        if name in image_map:
            return match.group("prefix") + image_map[name]
        if f"images/{name}" in tracked:
            raw_names.append(name)
            return match.group("prefix") + RAW_PREFIX + name
        warnings.append(f"untracked image (will not render on GitHub): {path}")
        return match.group(0)

    return IMG_RE.sub(repl, body), warnings, raw_names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="path to the Markdown file to publish")
    parser.add_argument("--dry-run", action="store_true", help="preview without calling GitHub")
    parser.add_argument("--force", action="store_true", help="publish even if the issue changed remotely")
    args = parser.parse_args()

    path = os.path.abspath(args.file)
    if not os.path.exists(path):
        sys.exit(f"file not found: {path}")

    text = open(path, encoding="utf-8").read()
    meta, _, rest = parse_front_matter(text)
    issue_number = meta.get("issue") if isinstance(meta.get("issue"), int) else None
    image_map = meta.get("images") if isinstance(meta.get("images"), dict) else {}

    h1_title, publish_body = split_title(rest)
    title = h1_title or meta.get("title") or os.path.splitext(os.path.basename(path))[0]
    title = str(title).strip()
    if not title:
        sys.exit("cannot determine a title")

    publish_body, warnings, raw_names = rewrite_images(publish_body, image_map, tracked_images())
    mode = f"update #{issue_number}" if issue_number else "create"

    print(f"file: {path}")
    print(f"mode: {mode}")
    print(f"title: {title}")
    print(f"body: {len(publish_body)} chars, {len(publish_body.splitlines())} lines")
    for name in image_map:
        print(f"image: {name} -> recorded URL")
    for name in raw_names:
        print(f"image: {name} -> raw GitHub URL")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if args.dry_run:
        print("dry-run: nothing published")
        return 0

    try:
        ensure_auth()
        if issue_number:
            remote = gh_json(
                ["issue", "view", str(issue_number), "--json", "number,title,url,state,createdAt,updatedAt,labels"]
            )
            local_updated = str(meta.get("updated", ""))
            remote_day = remote["updatedAt"][:10]
            if local_updated and remote_day > local_updated and not args.force:
                print(
                    f"conflict: issue #{issue_number} was updated remotely on {remote_day}, "
                    f"local copy on {local_updated}. Re-run with --force to overwrite."
                )
                return 3
            with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as tmp:
                tmp.write(publish_body)
                tmp_path = tmp.name
            try:
                gh(["issue", "edit", str(issue_number), "--title", title, "--body-file", tmp_path])
            finally:
                os.unlink(tmp_path)
            remote = gh_json(
                ["issue", "view", str(issue_number), "--json", "number,title,url,state,createdAt,updatedAt,labels"]
            )
        else:
            with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as tmp:
                tmp.write(publish_body)
                tmp_path = tmp.name
            try:
                out = gh(["issue", "create", "--title", title, "--body-file", tmp_path])
            finally:
                os.unlink(tmp_path)
            match = re.search(r"/issues/(\d+)", out)
            if not match:
                sys.exit(f"could not parse issue number from: {out}")
            issue_number = int(match.group(1))
            remote = gh_json(
                ["issue", "view", str(issue_number), "--json", "number,title,url,state,createdAt,updatedAt,labels"]
            )

        labels = [label["name"] for label in remote.get("labels") or []]
        updated_text = set_front_matter(
            text,
            {
                "issue": remote["number"],
                "title": remote["title"],
                "state": remote["state"],
                "created": remote["createdAt"][:10],
                "updated": remote["updatedAt"][:10],
                "url": remote["url"],
                "labels": labels,
            },
        )
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(updated_text)

        print(f"published: {remote['url']}")
        if raw_names:
            print("note: commit and push the new images before readers can see them")
        return 0
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())