# ig-frame-runner

採用ショートの自動編集の作業箱（`edit.yml` だけ）。受付（Render の recruit-shorts-mcp）が仕事の番号を渡して起こす。

- データ・鍵・依頼主の情報は置かない。指示は受付がドライブに署名つきで置き、作業箱が番号で取りに行く（読んだら消す）。
- ログに出すのは段の名前だけ（公開 repo のログは誰でも見られる）。
- 会員の動画を解く段は、鍵の無い別のユーザーで、AI の鍵だけを持って回す（2026-10-29 辛口点検）。
- 外の動画を測る作業（measure・frames）は IKEMENLTD/ig-measure-runner に分けた（2026-10-29）。Actions の使い回し（キャッシュ）は
  repo の中で共有されるので、信用できない動画を扱う作業と同じ repo に置かない。**この repo に他のワークフローを足さない。**
- 公開 repo にしているのは、組織の非公開 repo の Actions が課金の都合で動かないため（2026-10-23）。
- 仕組みの説明は IKEMENLTD/auto-video-edit の `docs/mcp-system.md`。
