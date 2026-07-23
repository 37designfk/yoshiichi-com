# 吉市水産 (yoshiichi.com)

WordPress から静的サイトへ移行済み。本番 yoshiichi.com は `public/` の静的ファイルを heteml で配信している。

## 構成

```
yoshiichi-com/
├── public/            # 本番 yoshiichi.com の実体（静的ファイル・日/英/中）
├── src/               # Astro（未使用。将来の再構築用に残置）
├── migration/         # WP抽出データ・変換スクリプト（データ類は .gitignore）
│   ├── rewrite_urls.py  # URL書き換え（SITE_PREFIX で出力先を切替）
│   ├── inject_switcher.py / build_translations.py / optimize_psi.py
│   ├── pages.json     # WP REST APIで取得した全固定ページ
│   ├── media.json     # メディアメタデータ
│   ├── mirror/        # 旧WPサイト全体のローカルミラー
│   └── wp-content/    # カスタムテーマのバックアップ
└── .github/workflows/pages.yml  # GH Pages（手動実行のみ・通常は使わない）
```

## Phase

- **Phase 1（完了）**: `public/` に日本語サイト静的ミラーを作成
- **Phase 2（完了）**: 多言語化（日/英/中）。`_lang/switcher.js` で言語切替
- **Phase 3（完了）**: 本番 yoshiichi.com を静的サイトへ切替（heteml ルート配信）

## デプロイ

本番は heteml へ rsync。**変更したファイルだけを送る**こと。

```
sshpass -p "$HETEML_PASSWORD" rsync -av \
  -e "ssh -o StrictHostKeyChecking=no -p 2222" --relative \
  ./index.html ./en/index.html ...  \
  kenfuruta0824@ssh-furuta.heteml.net:~/web/yoshiichi.com/
```

- 実行は `public/` 直下から。`--delete` は使わない（サーバー側に `api/` などリポジトリ管理外のディレクトリがある）
- 接続情報は `~/wordpress-management/CLAUDE.md`、パスワードは 1Password（Claude Code / heteml SSH）

### GitHub Pages（ステージング）

main への push での自動デプロイは停止済み。確認用に出したい場合のみ、
`SITE_PREFIX=/yoshiichi-com` で `migration/rewrite_urls.py` を回してから
Actions の "Deploy to GitHub Pages" を手動実行する。
プレフィックスなしのまま出すと CSS・画像が 404 になる。

## 本番サイト

- heteml（users266.vip.heteml.jp）の `~/web/yoshiichi.com/` に静的配信
- 旧WordPress一式は `~/web/yoshiichi.com_wp_old_20260507/` に退避
- デザイン元テーマ: Arkhe + Yoshiichi-suisan子テーマ（37design製）
