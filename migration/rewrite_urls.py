#!/usr/bin/env python3
"""ミラーしたHTMLの絶対URLを相対URLに書き換える"""
import pathlib, re, urllib.parse

MIRROR = pathlib.Path(__file__).parent / "mirror"
DIST = pathlib.Path(__file__).parent.parent / "public"
DIST.mkdir(exist_ok=True)

BASE = "https://yoshiichi.com"

def rewrite(text):
    # 絶対URL → 相対に
    text = text.replace("https://yoshiichi.com", "")
    text = text.replace("http://yoshiichi.com", "")
    text = text.replace("//yoshiichi.com", "")
    # ファビコン/JSONLD等の別サイトURLは残す
    return text


def copy_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in (".html", ".css", ".js", ".xml", ".json", ".svg"):
        try:
            text = src.read_text("utf-8", errors="ignore")
            dst.write_text(rewrite(text), "utf-8")
        except Exception:
            dst.write_bytes(src.read_bytes())
    else:
        dst.write_bytes(src.read_bytes())


def main():
    EXCLUDE = {"wp-json", "feed", "comments", "sample-page"}
    for src in MIRROR.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(MIRROR)
        # wp-jsonなど除外
        if any(part in EXCLUDE for part in rel.parts):
            continue
        dst = DIST / rel
        copy_file(src, dst)
    print(f"Copied to {DIST}")


if __name__ == "__main__":
    main()
