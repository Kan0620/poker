# Poker Range Trainer

テキサスホールデム用のプリフロップ＆フロップ練習ツールです。
ブラウザからアクセスして、各種ポーカーシチュエーションをクイズ形式で学習できます。

**🌐 本番環境**: https://poker-166214121232.asia-southeast1.run.app

## 🎯 学習モード

### プリフロップモード

1. **オープンレンジ** - ポジション別のオープン判断（UTG〜BTN）
2. **SB open** - SB first-in時のRAISE/LIMP/FOLD判断
3. **3bet** - 相手のオープンに対する3bet判断（複数アクション選択可）
4. **3betディフェンス** - 相手の3betに対するディフェンス判断（IP/OOP考慮）
5. **BB defence** - BBでのCALL/FOLD判断（相手ポジション別）
6. **パワーナンバー** - ショートスタック時のオールイン判断（M値ベース）

### ポストフロップモード

7. **MDF Trainer** - フロップでのMDF（Minimum Defense Frequency）判断練習
   - レンジ × ボードのバケット分布を理解
   - Bet sizeに応じた適切なdefend範囲を学習
   - 10秒タイマー付き

### その他

8. **MIX** - 上記7モードをランダムに出題

## 🏗️ プロジェクト構造

```
poker/
├── main.py (8行)              # FastAPIアプリのエントリーポイント
├── templates/
│   └── index.html            # UI全体（Jinja2テンプレート）
├── core/                     # コアロジック・レンジ判定
│   ├── enums.py              # StudyMode, Position, Bucket定義
│   ├── ranks.py              # RANK_TO_STRマッピング
│   ├── utils_hand.py         # hand_label, random_hand等
│   ├── cards.py              # カード生成・ボード生成（MDF用）
│   ├── ranges_open.py        # オープンレンジ判定
│   ├── ranges_3bet.py        # 3betレンジ判定
│   ├── ranges_3bet_defence.py # 3betディフェンスレンジ判定
│   ├── ranges_bb_defence.py  # BB defenceレンジ判定
│   ├── ranges_sb_open.py     # SB first-in判定
│   ├── power_number.py       # パワーナンバー計算
│   └── range_combos.py       # レンジ→コンボセット変換（MDF用）
├── mdf/                      # MDF Trainer関連
│   ├── evaluator.py          # evaluate_hand_strength（バケット分類）
│   └── analysis.py           # calculate_mdf_analysis（MDF計算）
├── quiz/                     # 問題生成
│   └── generators.py         # 全モードの問題生成関数
├── web/                      # HTTPルーティング
│   └── routes.py             # FastAPI APIRouter（GET /, POST /answer）
└── Dockerfile                # 本番デプロイ用
```

### アーキテクチャ原則

- **3層構造**: HTTP層（web/） → 問題生成層（quiz/） → ロジック層（core/, mdf/）
- **循環依存の回避**: core/enums.pyが最下層、webが最上層
- **疎結合**: 各モジュールは独立してテスト可能
- **シンプルさ優先**: 過度な抽象化を避け、読みやすさを重視

## 🚀 ローカル開発

### 依存関係のインストール

```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### 開発サーバー起動

```bash
# ホットリロード有効
uvicorn main:app --reload

# または特定のホスト・ポートで起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### アクセス

- ローカル: http://localhost:8000

## 🐳 Docker開発

### イメージのビルド

```bash
docker build -t poker-trainer .
```

### コンテナの実行

```bash
# ポート8080で公開
docker run -p 8080:8080 poker-trainer

# 開発用（ボリュームマウント）
docker run -p 8080:8080 -v $(pwd):/app poker-trainer
```

### アクセス

- Docker: http://localhost:8080

## 📦 本番デプロイ（Google Cloud Run）

### イメージのビルド＆プッシュ

```bash
# マルチプラットフォーム対応
docker buildx build --platform linux/amd64 \
  -t asia-southeast1-docker.pkg.dev/poker-481112/poker/poker:latest \
  --push .
```

### Cloud Runにデプロイ

```bash
gcloud run deploy poker \
  --image asia-southeast1-docker.pkg.dev/poker-481112/poker/poker \
  --region=asia-southeast1 \
  --cpu=8 --memory=32Gi \
  --timeout=3600 \
  --concurrency=1 \
  --cpu-boost \
  --min-instances=0 \
  --max-instances=1 \
  --ingress=all
```

## 🔍 デバッグ用コマンド

ローカルで本番イメージの動作確認：

```bash
# イメージのビルド（ローカル用）
docker build -t asia-southeast1-docker.pkg.dev/poker-481112/poker/poker:latest .

# ローカルで実行テスト（ポート8080で起動）
docker run --rm --env PORT=8080 -p 8080:8080 \
  asia-southeast1-docker.pkg.dev/poker-481112/poker/poker:latest
```

## 📚 技術スタック

- **バックエンド**: FastAPI (Python 3.11)
- **テンプレート**: Jinja2
- **フロントエンド**: HTML + CSS + Vanilla JS（ミニマル設計）
- **デプロイ**: Docker + Google Cloud Run

## 🎲 設計思想

このプロジェクトは**GTOソルバー**ではなく、ユーザーが決めた**簡易レンジルールを体に染み込ませるトレーナー**です。

- 多少のGTOとのズレよりも、「覚えやすい一貫したルール」を優先
- バケット定義の一貫性を最優先（実装者が迷わない明確なルール）
- 実戦で使える「パッと判断できる基準」の習得を目指す

## 📖 開発ガイド

詳細な開発ガイドラインは [CLAUDE.md](CLAUDE.md) を参照してください。

- 新しいレンジロジックの実装方法
- ファイル構成と責務
- 各モードの実装詳細
- UI/UXガイドライン

## 🔗 関連リンク

- [CLAUDE.md](CLAUDE.md) - Claude Code向け開発ガイドライン（日本語）
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)

## 📝 ライセンス

Private Project
