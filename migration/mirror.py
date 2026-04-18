#!/usr/bin/env python3
"""yoshiichi.com 全体をダウンロード"""
import os, re, sys, urllib.parse, urllib.request, pathlib, time
from html.parser import HTMLParser

BASE = "https://yoshiichi.com"
OUT = pathlib.Path(__file__).parent / "mirror"
OUT.mkdir(exist_ok=True)

visited_pages = set()
visited_assets = set()
queue = []

PAGE_SLUGS = [
    "/",
    "/事業案内/",
    "/会社概要/",
    "/会社沿革/",
    "/企業理念/",
    "/商品紹介/",
    "/お取引をご希望の皆様へ/",
    "/お問い合わせ/",
    "/新着情報/",
]


class AssetExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src", "poster", "data-src"):
            if key in a and a[key]:
                self.assets.append(a[key])
        if tag == "source" and "srcset" in a:
            for part in a["srcset"].split(","):
                url = part.strip().split(" ")[0]
                if url:
                    self.assets.append(url)


def normalize(url, base):
    if url.startswith(("data:", "mailto:", "tel:", "javascript:", "#")):
        return None
    absolute = urllib.parse.urljoin(base, url)
    parsed = urllib.parse.urlparse(absolute)
    if parsed.netloc and parsed.netloc != urllib.parse.urlparse(BASE).netloc:
        return None
    return parsed._replace(fragment="").geturl()


def url_to_path(url):
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path)
    if path.endswith("/") or path == "":
        path = path + "index.html"
    return OUT / path.lstrip("/")


def download(url, is_page=False):
    target = url_to_path(url)
    if target.exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        target.write_bytes(data)
        return target
    except Exception as e:
        print(f"  ERROR {url}: {e}", file=sys.stderr)
        return None


def extract_from_html(html, base_url):
    parser = AssetExtractor()
    parser.feed(html)
    # Also find url() in inline style attrs and <style>
    urls = list(parser.assets)
    urls += re.findall(r"url\(([^)]+)\)", html)
    normalized = []
    for u in urls:
        u = u.strip().strip('"').strip("'")
        n = normalize(u, base_url)
        if n:
            normalized.append(n)
    return normalized


def process_css(path, base_url):
    try:
        text = path.read_text("utf-8", errors="ignore")
    except Exception:
        return []
    urls = re.findall(r"url\(([^)]+)\)", text)
    imports = re.findall(r'@import\s+["\']([^"\']+)["\']', text)
    return [normalize(u.strip().strip('"').strip("'"), base_url) for u in urls + imports if u]


def main():
    for slug in PAGE_SLUGS:
        queue.append(BASE + slug)

    while queue:
        url = queue.pop(0)
        if url in visited_pages:
            continue
        visited_pages.add(url)
        print(f"PAGE: {url}")
        target = download(url)
        if not target or not target.suffix in ("", ".html"):
            continue
        html = target.read_text("utf-8", errors="ignore")
        for asset in extract_from_html(html, url):
            if asset in visited_assets:
                continue
            visited_assets.add(asset)
            print(f"  asset: {asset}")
            asset_path = download(asset)
            if asset_path and asset_path.suffix.lower() == ".css":
                # CSSの中のassetも
                for css_asset in process_css(asset_path, asset):
                    if css_asset and css_asset not in visited_assets:
                        visited_assets.add(css_asset)
                        print(f"  css-asset: {css_asset}")
                        download(css_asset)

    print(f"\nDone. {len(visited_pages)} pages, {len(visited_assets)} assets")


if __name__ == "__main__":
    main()
