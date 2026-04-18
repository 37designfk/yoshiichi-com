#!/usr/bin/env python3
"""PSI最適化: 不要スクリプト削除 + CSS非同期化 + preconnect追加"""
import pathlib, re

PUBLIC = pathlib.Path(__file__).parent.parent / "public"

# 全ページで削除する JS（未使用 or モダン環境で不要）
REMOVE_JS_GLOBAL = [
    "jquery-migrate.min.js",
    "ScrollTrigger.min.js",
    "TextPlugin.min.js",
]

# フォームが無いページで削除する JS/CSS
REMOVE_FORM_ASSETS_JS = [
    "wp-hooks.min.js",
    "wp-i18n.min.js",
    "contact-form-7/includes/swv/js/index.js",
    "contact-form-7/includes/js/index.js",
]
REMOVE_FORM_ASSETS_CSS = [
    "contact-form-7/includes/css/styles.css",
]

# フォームありページ（index.html / contact / business-inquiry）
FORM_PAGES_KEYWORDS = ["contact-form-7", "wpcf7"]


def has_form(html: str) -> bool:
    return any(k in html for k in FORM_PAGES_KEYWORDS) and 'wpcf7-form' in html


def remove_script_tags(html: str, patterns: list) -> str:
    for pat in patterns:
        # <script ...src="...pat..." ...></script> を丸ごと削除
        html = re.sub(
            rf'<script[^>]*src=[\'"][^\'"]*{re.escape(pat)}[^\'"]*[\'"][^>]*>\s*</script>\s*',
            '', html
        )
    return html


def remove_link_tags(html: str, patterns: list) -> str:
    for pat in patterns:
        html = re.sub(
            rf'<link[^>]*href=[\'"][^\'"]*{re.escape(pat)}[^\'"]*[\'"][^>]*/?>',
            '', html
        )
    return html


def remove_inline_i18n_blocks(html: str) -> str:
    """wp-i18n-js-after / contact-form-7-js-translations のinline scriptも削除"""
    html = re.sub(
        r'<script[^>]*id=[\'"](?:wp-i18n-js-after|contact-form-7-js-translations|contact-form-7-js-after)[\'"][^>]*>.*?</script>',
        '', html, flags=re.DOTALL
    )
    return html


def defer_scripts(html: str) -> str:
    """src付きscriptに defer を追加（既に defer/async なければ）"""
    def repl(m):
        tag = m.group(0)
        if ' defer' in tag or ' async' in tag or 'type="module"' in tag:
            return tag
        return tag[:-1] + ' defer>' if tag.endswith('>') else tag
    return re.sub(r'<script[^>]+src=[\'"][^\'"]+[\'"][^>]*>', repl, html)


def async_css(html: str) -> str:
    """render-blocking CSS を preload swap パターンに変換
    重要CSSとしてArkhe main.cssは残す（FV用スタイル）"""
    CRITICAL = {
        "arkhe/dist/css/main.css",
        "Yoshiichi-suisan/style.css",
        "_lang/switcher.css",
    }
    def is_critical(url: str) -> bool:
        return any(c in url for c in CRITICAL)

    def repl(m):
        tag = m.group(0)
        href_m = re.search(r'href=[\'"]([^\'"]+)[\'"]', tag)
        if not href_m:
            return tag
        href = href_m.group(1)
        if is_critical(href):
            return tag
        # 非クリティカル: preload → onload で stylesheet に切替
        return (
            f'<link rel="preload" href="{href}" as="style" '
            f'onload="this.onload=null;this.rel=\'stylesheet\'">'
            f'<noscript><link rel="stylesheet" href="{href}"></noscript>'
        )
    return re.sub(r'<link[^>]*rel=[\'"]stylesheet[\'"][^>]*>', repl, html)


def add_preconnect(html: str) -> str:
    """yoshiichi.com (画像直リン) 用の preconnect 追加"""
    if 'rel="preconnect" href="https://yoshiichi.com"' in html:
        return html
    marker = '<link rel=\'dns-prefetch\' href=\'//cdnjs.cloudflare.com\' />'
    injection = (
        '<link rel="preconnect" href="https://yoshiichi.com" crossorigin>'
        '<link rel="dns-prefetch" href="https://yoshiichi.com">'
    )
    if marker in html:
        return html.replace(marker, injection + marker, 1)
    # <meta name='robots'…> の直前に挿入
    return html.replace("</head>", injection + "</head>", 1)


def process(html_path: pathlib.Path):
    html = html_path.read_text("utf-8")
    is_form_page = has_form(html)

    # 1. グローバル不要JS削除
    html = remove_script_tags(html, REMOVE_JS_GLOBAL)

    # 2. フォーム無しページではCF7関連も削除
    if not is_form_page:
        html = remove_script_tags(html, REMOVE_FORM_ASSETS_JS)
        html = remove_link_tags(html, REMOVE_FORM_ASSETS_CSS)
        html = remove_inline_i18n_blocks(html)

    # 3. preconnect 追加
    html = add_preconnect(html)

    # 4. CSS非同期化
    html = async_css(html)

    # 5. Script defer 付与
    html = defer_scripts(html)

    html_path.write_text(html, "utf-8")


def main():
    count = 0
    for html in PUBLIC.rglob("index.html"):
        process(html)
        count += 1
    print(f"Optimized {count} pages")


if __name__ == "__main__":
    main()
