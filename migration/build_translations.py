#!/usr/bin/env python3
"""JP ページから EN/ZH の翻訳版ページを生成"""
import pathlib, json, shutil, urllib.parse

ROOT = pathlib.Path(__file__).parent.parent
PUBLIC = ROOT / "public"
TRANS_FILE = ROOT / "migration" / "translations.json"

# JP slug (URL-encoded or raw) → EN/ZH slug
JP_TO_SLUG = {
    "事業概要": "services",
    "%e4%ba%8b%e6%a5%ad%e6%a6%82%e8%a6%81": "services",
    "会社概要": "about",
    "%e4%bc%9a%e7%a4%be%e6%a6%82%e8%a6%81": "about",
    "会社沿革": "history",
    "%e4%bc%9a%e7%a4%be%e6%b2%bf%e9%9d%a9": "history",
    "企業理念": "philosophy",
    "%e4%bc%81%e6%a5%ad%e7%90%86%e5%bf%b5": "philosophy",
    "お問い合わせ": "contact",
    "%e3%81%8a%e5%95%8f%e3%81%84%e5%90%88%e3%82%8f%e3%81%9b": "contact",
    "取引をご希望の皆様へ": "business-inquiry",
    "%e5%8f%96%e5%bc%95%e3%82%92%e3%81%94%e5%b8%8c%e6%9c%9b%e3%81%ae%e7%9a%86%e6%a7%98%e3%81%b8": "business-inquiry",
}

# ディレクトリ名 → 出力スラグ
DIR_TO_SLUG = {
    "": "",  # トップ
    "事業概要": "services/",
    "会社概要": "about/",
    "会社沿革": "history/",
    "企業理念": "philosophy/",
    "お問い合わせ": "contact/",
    "取引をご希望の皆様へ": "business-inquiry/",
}


def rewrite_internal_links(html: str, lang: str) -> str:
    """内部nav linkを /en/ or /zh/ 用のものに書き換え"""
    prefix = "/yoshiichi-com"
    # 各 JP slug を /{lang}/{slug}/ に置換
    for jp, slug in JP_TO_SLUG.items():
        # URL エンコード済み
        html = html.replace(
            f'href="{prefix}/{jp}/"',
            f'href="{prefix}/{lang}/{slug}/"',
        )
    # ルート (/) も /{lang}/ に
    html = html.replace(
        f'href="{prefix}/"',
        f'href="{prefix}/{lang}/"',
    )
    # ロゴ等の `/yoshiichi-com/"` も同様
    return html


def apply_translations(html: str, lang: str, translations: dict) -> str:
    """翻訳辞書を適用"""
    # 長い文字列から順に置換（短い方が部分マッチしてしまうのを避ける）
    strings = translations["strings"]
    for jp in sorted(strings.keys(), key=len, reverse=True):
        tr = strings[jp].get(lang)
        if tr is None or tr == "":
            continue
        # XML エンティティ（&#8211; など）を含む可能性にも対応
        html = html.replace(jp, tr)
    return html


def update_html_lang(html: str, lang: str) -> str:
    """<html lang="ja"> を書き換え"""
    lang_attr = "zh-CN" if lang == "zh" else lang
    html = html.replace('<html lang="ja"', f'<html lang="{lang_attr}"')
    return html


# EN版でも特別な洋文タイポを当てたい見出し（マーカー文字列 → 追加クラス）
WESTERN_DISPLAY_MARKERS_EN = [
    "Leveraging the eye and skill we have cultivated in Akashi",
]


def add_display_classes(html: str, lang: str) -> str:
    """EN版の特定見出しに洋文タイポ用クラスを付与"""
    if lang != "en":
        return html
    for marker in WESTERN_DISPLAY_MARKERS_EN:
        html = html.replace(
            f'<h2 class="ark-block-heading__main">{marker}',
            f'<h2 class="ark-block-heading__main is-en-display">{marker}',
        )
    return html


def build_lang_dir(lang: str, translations: dict):
    """/en/ or /zh/ ディレクトリを構築"""
    out_dir = PUBLIC / lang
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # JP ページを走査
    for jp_dir_name, out_slug in DIR_TO_SLUG.items():
        src_dir = PUBLIC if jp_dir_name == "" else PUBLIC / jp_dir_name
        src_html = src_dir / "index.html"
        if not src_html.exists():
            print(f"  SKIP: {src_html} not found")
            continue

        html = src_html.read_text("utf-8")
        html = rewrite_internal_links(html, lang)
        html = apply_translations(html, lang, translations)
        html = update_html_lang(html, lang)
        html = add_display_classes(html, lang)

        dst = out_dir / out_slug / "index.html" if out_slug else out_dir / "index.html"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(html, "utf-8")
        print(f"  {lang}: {dst.relative_to(PUBLIC)}")


def main():
    translations = json.loads(TRANS_FILE.read_text("utf-8"))
    for lang in ("en", "zh"):
        print(f"\nBuilding {lang}/")
        build_lang_dir(lang, translations)
    print("\nDone.")


if __name__ == "__main__":
    main()
