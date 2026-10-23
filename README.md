# ig-frame-runner

作業用のランナー。渡された動画の URL から、1本ごとのコマ一覧（画が変わった所・秒つき）を作って、1日で消える artifact に置くだけ。

- データ・鍵・依頼主の情報は置かない。URL は実行のたびに `workflow_dispatch` の入力で渡す。
- 公開 repo にしているのは、組織の非公開 repo の Actions が課金の都合で動かないため（2026-10-23）。
- 使い方は IKEMENLTD/auto-video-edit の `skills/account-edit-analysis/`。
