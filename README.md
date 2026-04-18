# 吉市水産 (yoshiichi.com) 移行プロジェクト

WordPress → Astro 移行のステージング環境。

## 構成

```
yoshiichi-com/
├── public/            # GH Pagesへデプロイされる静的ファイル（現WPサイトのミラー）
├── src/               # Astro（Phase 2で多言語化に使用）
├── migration/         # WP抽出データ（.gitignore）
│   ├── pages.json     # WP REST APIで取得した全固定ページ
│   ├── media.json     # メディアメタデータ
│   ├── mirror/        # 現サイト全体のローカルミラー
│   └── wp-content/    # カスタムテーマのバックアップ
└── .github/workflows/pages.yml  # GH Pagesデプロイ
```

## Phase

- **Phase 1（現在）**: `public/` に日本語サイト静的ミラー。GH Pagesにデプロイ。本番 yoshiichi.com は未変更
- **Phase 2**: Astroで i18n（日/英/中）、デザイン・動きは完全踏襲
- **Phase 3**: 本番 yoshiichi.com へ切替

## デプロイ

`main` ブランチにpushで自動デプロイ。URL: https://37designfk.github.io/yoshiichi-com/

## 本番サイト

- WordPress on heteml（users266.vip.heteml.jp）
- テーマ: Arkhe + Yoshiichi-suisan子テーマ（37design製）
