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


PUBLIC_BASE = pathlib.Path(__file__).parent.parent / "public"

# インライン化する小さなCSS（render-blockingを無くすため）
INLINE_CSS_PATHS = {
    "_lang/switcher.css": "_lang/switcher.css",
    "Yoshiichi-suisan/style.css": "wp-content/themes/Yoshiichi-suisan/style.css",
}


def async_css(html: str) -> str:
    """render-blocking CSS を preload swap or inline で除去"""
    # 1) インライン化対象のCSS
    for key, rel_path in INLINE_CSS_PATHS.items():
        css_file = PUBLIC_BASE / rel_path
        if not css_file.exists():
            continue
        css_body = css_file.read_text("utf-8")
        # <link ...href="...key..." ...> を探して inline <style> に置換
        pattern = rf'<link[^>]*href=[\'"][^\'"]*{re.escape(key)}[^\'"]*[\'"][^>]*/?>'
        inline_tag = f'<style data-inlined="{key}">{css_body}</style>'
        html = re.sub(pattern, inline_tag, html, count=1)

    # 2) 残りの全CSS を preload swap に
    def repl(m):
        tag = m.group(0)
        href_m = re.search(r'href=[\'"]([^\'"]+)[\'"]', tag)
        if not href_m:
            return tag
        href = href_m.group(1)
        return (
            f'<link rel="preload" href="{href}" as="style" '
            f'onload="this.onload=null;this.rel=\'stylesheet\'">'
            f'<noscript><link rel="stylesheet" href="{href}"></noscript>'
        )
    return re.sub(r'<link[^>]*rel=[\'"]stylesheet[\'"][^>]*>', repl, html)


def add_preconnect(html: str) -> str:
    """yoshiichi.com (画像直リン) 用の preconnect + hero動画のpreload追加"""
    if 'rel="preconnect" href="https://yoshiichi.com"' in html:
        return html
    marker = '<link rel=\'dns-prefetch\' href=\'//cdnjs.cloudflare.com\' />'
    injection = (
        '<link rel="preconnect" href="https://yoshiichi.com" crossorigin>'
        '<link rel="dns-prefetch" href="https://yoshiichi.com">'
    )
    if marker in html:
        return html.replace(marker, injection + marker, 1)
    return html.replace("</head>", injection + "</head>", 1)


def remove_wp_bloat(html: str) -> str:
    """WP固有のinline scriptで不要なものを削除"""
    # Speculation rules (prefetch) — ほぼ効果ないのに容量食う
    html = re.sub(
        r'<script[^>]*type=[\'"]speculationrules[\'"][^>]*>.*?</script>',
        '', html, flags=re.DOTALL
    )
    # wp-emoji関連
    html = re.sub(
        r'<script[^>]*id=[\'"]wp-emoji[^\'"]*[\'"][^>]*>.*?</script>',
        '', html, flags=re.DOTALL
    )
    # WordPress oEmbed discovery links (不要)
    html = re.sub(
        r'<link[^>]*type=[\'"]application/json\+oembed[\'"][^>]*/?>',
        '', html
    )
    html = re.sub(
        r'<link[^>]*type=[\'"]text/xml\+oembed[\'"][^>]*/?>',
        '', html
    )
    # RSS/feed alternate link (staging不要)
    html = re.sub(
        r'<link[^>]*rel=[\'"]alternate[\'"][^>]*type=[\'"]application/rss\+xml[\'"][^>]*/?>',
        '', html
    )
    return html


def optimize_hero_video(html: str) -> str:
    """hero video に preload=auto + poster 付与（LCP改善）"""
    # FV curtain の compo2.mp4
    html = html.replace(
        '<video class="mp4-content" autoplay loop muted playsinline>',
        '<video class="mp4-content" autoplay loop muted playsinline preload="auto" fetchpriority="high">'
    )
    return html


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

    # 3. WP固有のbloat削除
    html = remove_wp_bloat(html)

    # 4. preconnect + hero video preload
    html = add_preconnect(html)
    html = optimize_hero_video(html)

    # 5. CSS非同期化
    html = async_css(html)

    # 6. Script defer 付与
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
