#!/usr/bin/env python3
"""全ページの<head>に言語スイッチャーのCSS/JSを注入"""
import pathlib, re

PUBLIC = pathlib.Path(__file__).parent.parent / "public"

SWITCHER_TAGS = """
<link rel="stylesheet" href="/yoshiichi-com/_lang/switcher.css">
<script src="/yoshiichi-com/_lang/switcher.js" defer></script>
""".strip()

def inject(html_file):
    text = html_file.read_text("utf-8", errors="ignore")
    if "switcher.css" in text:
        return False  # 既に注入済み
    # </head> の直前に挿入
    new_text = text.replace("</head>", f"{SWITCHER_TAGS}\n</head>", 1)
    if new_text == text:
        return False
    html_file.write_text(new_text, "utf-8")
    return True

count = 0
for html in PUBLIC.rglob("index.html"):
    if inject(html):
        count += 1
        print(f"  injected: {html.relative_to(PUBLIC)}")
print(f"\nInjected {count} pages")
