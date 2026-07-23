#!/usr/bin/env python3
"""ミラーしたHTMLの絶対URLを相対URLに書き換える"""
import pathlib, re, urllib.parse

MIRROR = pathlib.Path(__file__).parent / "mirror"
DIST = pathlib.Path(__file__).parent.parent / "public"
DIST.mkdir(exist_ok=True)

BASE = "https://yoshiichi.com"
# 本番 yoshiichi.com (heteml ルート) はプレフィックスなしがデフォルト。
# GH Pages ステージング (37designfk.github.io/yoshiichi-com/) に出すときは
# SITE_PREFIX=/yoshiichi-com を環境変数で指定する。
import os, re
PREFIX = os.environ.get("SITE_PREFIX", "")

def rewrite(text):
    # まず yoshiichi.com 絶対URLをプレフィックス付き相対にする
    text = text.replace("https://yoshiichi.com", PREFIX)
    text = text.replace("http://yoshiichi.com", PREFIX)
    text = text.replace("//yoshiichi.com", PREFIX)
    # GH Pages 配信時のみ uploads を live 直リンクに戻す（GH Pages にメディアを置かないため）。
    # heteml ルート (PREFIX="") の場合は uploads も同一オリジンに揃えておく。
    if PREFIX:
        text = text.replace(f"{PREFIX}/wp-content/uploads/", "https://yoshiichi.com/wp-content/uploads/")
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
        # /wp-content/uploads/ はリポに含めない（直リンクでlive参照）
        if "uploads" in rel.parts and "wp-content" in rel.parts:
            continue
        dst = DIST / rel
        copy_file(src, dst)
    print(f"Copied to {DIST}")


if __name__ == "__main__":
    main()
