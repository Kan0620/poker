# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 言語設定

**このプロジェクトでは、Claude との会話は日本語で行ってください。**

コード内のコメント、変数名、関数名は英語でも構いませんが、
ユーザーとのやり取り、説明、質問、提案などは**すべて日本語で**お願いします。

---

# Claude 開発ガイドライン（poker-range-trainer）

このリポジトリは、テキサスホールデム用の **プリフロップ練習ツール** です。
ブラウザからアクセスして、以下のモードでクイズ形式に学習できます。

- オープンレンジ（UTG〜BTN + SB first-in）
- 3betレンジ
- 3betディフェンスレンジ
- パワーナンバー（ショートスタック時のオールイン判断）
- BB defence（BBでのCALLレンジ）
- **MDF Trainer（フロップでのMDF判断練習）** ← 新規追加
- MIX（上記6モードのランダム）

バックエンドは **FastAPI（Python）**、フロントは **シンプルなHTML＋Jinja2** です。

---

## 開発コマンド

### ローカル開発
```bash
# 依存関係のインストール
pip install fastapi uvicorn jinja2 python-multipart

# 開発サーバー起動（ホットリロード有効）
uvicorn main:app --reload

# または特定のホスト・ポートで起動
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker開発
```bash
# イメージのビルド
docker build -t poker-trainer .

# コンテナの実行（ポート8080で公開）
docker run -p 8080:8080 poker-trainer

# 開発用（ボリュームマウント）
docker run -p 8080:8080 -v $(pwd):/app poker-trainer
```

### アクセス
- ローカル: http://localhost:8000
- Docker: http://localhost:8080

### デプロイ（Google Cloud Run）

本番環境へのデプロイ手順：

```bash
# マルチプラットフォーム対応のイメージをビルド＆プッシュ
docker buildx build --platform linux/amd64 \
  -t asia-southeast1-docker.pkg.dev/poker-481112/poker/poker:latest \
  --push .

# Cloud Runにデプロイ
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

### デバッグ用コマンド

ローカルで本番イメージの動作確認：

```bash
# イメージのビルド（ローカル用）
docker build -t asia-southeast1-docker.pkg.dev/poker-481112/poker/poker:latest .

# ローカルで実行テスト（ポート8080で起動）
docker run --rm --env PORT=8080 -p 8080:8080 \
  asia-southeast1-docker.pkg.dev/poker-481112/poker/poker:latest
```

---

## 技術スタック & ファイル構成

### プロジェクト構造

```
poker/
├── main.py (8行) - FastAPIアプリのエントリーポイント
├── templates/
│   └── index.html - Jinja2テンプレート（UI全体）
├── core/ - コアロジック・レンジ判定
│   ├── enums.py - StudyMode, Position, Bucket定義
│   ├── ranks.py - RANK_TO_STR マッピング
│   ├── utils_hand.py - hand_label, random_hand等
│   ├── cards.py - カード生成・ボード生成（MDF用）
│   ├── ranges_open.py - オープンレンジ判定
│   ├── ranges_3bet.py - 3betレンジ判定
│   ├── ranges_3bet_defence.py - 3betディフェンスレンジ判定
│   ├── ranges_bb_defence.py - BB defenceレンジ判定
│   ├── ranges_sb_open.py - SB first-in判定
│   ├── power_number.py - パワーナンバー計算
│   └── range_combos.py - レンジ→コンボセット変換（MDF用）
├── mdf/ - MDF Trainer関連
│   ├── evaluator.py - evaluate_hand_strength（バケット分類）
│   └── analysis.py - calculate_mdf_analysis（MDF計算）
├── quiz/ - 問題生成
│   └── generators.py - 全モードの問題生成関数
├── web/ - HTTPルーティング
│   └── routes.py - FastAPI APIRouter（GET /, POST /answer）
└── Dockerfile - 本番デプロイ用
```

### ファイル責務

**main.py (8行)**
- FastAPIアプリ初期化
- APIRouterの登録のみ

**core/** - ビジネスロジック層
- レンジ判定ルールの実装
- ハンドユーティリティ
- パワーナンバー計算
- 依存関係: なし（純粋なロジック層）

**mdf/** - MDF Trainer専用ロジック
- バケット分類（Monster / Strong Made / Weak Made / Draw / SD Value / Air）
- MDF計算とカットオフ決定
- 依存関係: core.enums, core.ranks, core.cards

**quiz/** - 問題生成層
- 各モードの問題生成ロジック
- 依存関係: core.*, mdf.*

**web/** - HTTPインターフェース層
- FastAPI APIRouter
- リクエスト処理、バリデーション
- テンプレートレンダリング
- 依存関係: quiz.generators

**templates/index.html**
- Jinja2テンプレート
- モード選択、問題表示、回答フォーム、結果表示
- 不正解時のレンジ表表示
- 10秒タイマー（MDF Trainer専用）

### アーキテクチャ原則

1. **責任分離**: HTTP層 → 問題生成層 → ロジック層の3層構造
2. **循環依存の回避**: core/enums.py が最下層、webが最上層
3. **疎結合**: 各モジュールは独立してテスト可能
4. **シンプルさ優先**: 過度な抽象化を避け、読みやすさを重視

**前提**：
このプロジェクトは「GTO ソルバー」ではなく、
ユーザーが決めた **簡易レンジルールを体に染み込ませるトレーナー** です。
多少のGTOとのズレよりも、「ユーザーが覚えやすい一貫したルール」を優先します。

---

## アーキテクチャの重要ポイント

### データフローとステート管理

アプリケーションは **ステートレス** な設計です：

1. **GET /** - 新しい問題を生成して表示
   - クエリパラメータ `mode` でモード選択
   - サーバー側で `generate_question(mode)` を呼び出し
   - 正解アクション (`correct_action`) は問題データに含まれる

2. **POST /answer** - 回答を検証して次の問題を表示
   - フォームの hidden フィールドで問題情報を受け取る
   - `user_action` (ラジオボタン) または `user_actions` (チェックボックス) で回答
   - サーバー側で正解判定
   - `last_result` として前回の結果を返す
   - `requested_mode` で次の問題のモードを保持（MIX対応）

### ハンド表現の内部仕様

- ハンドは `(hand_hi, hand_lo, suited)` の3値で管理
  - `hand_hi`: 14 (A) 〜 2 の整数（常に `hand_hi >= hand_lo`）
  - `hand_lo`: 14 (A) 〜 2 の整数
  - `suited`: True/False（ペアの場合は意味なし）

- 表示用ラベルは `hand_label(hi, lo, suited)` で生成
  - 例: `"AKs"`, `"AKo"`, `"TT"`

### レンジ判定の階層構造

各モードごとに判定関数が分離されている：

1. **オープンレンジ**: `in_open_range(pos, hi, lo, suited)`
   - ポジション別の関数に委譲: `in_utg_open_range()`, `in_utg12_open_range()`, etc.
   - 各ポジションのルールは独立して実装
   - **SB first-in**: `sb_first_in_action(hi, lo, suited)`
     - BTNレンジに入る → `"raise"`
     - オフスート → `"fold"`
     - スーテッドで下≤3 → `"fold"`
     - 残りスーテッド → `"limp"`

2. **3betレンジ**: `three_bet_allowed_actions(hero_pos, villain_pos, hi, lo, suited)`
   - 返り値: `["3bet"]`, `["call"]`, `["3bet", "call"]`, `["fold"]` など
   - 複数アクション許容のケースに対応

3. **3betディフェンス**: `three_bet_defence_action(hero_pos, in_position, hi, lo, suited)`
   - IP/OOP の判定が重要
   - 返り値: `"defend"` または `"fold"`

4. **パワーナンバー**: `should_shove_with_power_number(hero_pos, hi, lo, suited, m_value)`
   - `assign_power_number()` でハンドに PN を割り当て
   - 公式: `PN × 後ろ人数 >= M × 後ろ人数` で shove/fold 判定

5. **BB defence**: `bb_defence_vs_open(villain_pos, hi, lo, suited)`
   - VillainポジションごとにCALLレンジが異なる
   - 返り値: `True` (defend) または `False` (fold)
   - vs UTG: タイトなレンジ（AQo+, ATs+, 66+等）
   - vs CO/BTN: ワイドなレンジ（A8o+, 全Axs, 22+等）

6. **MDF Trainer**: `calculate_mdf_analysis(range_combos, board, bet_size)`
   - レンジ × ボード から全コンボを列挙し、ボードとの重複を除外
   - 各コンボをバケット分類（Monster / Strong Made / Weak Made / Draw / SD Value / Air）
   - MDF = 1 / (1 + bet_size) を計算
   - 強い順から累積して、MDFを満たすカットオフバケットを特定
   - Mix必要時は割合も計算

### MIXモードの実装

`StudyMode.MIX` が選択された場合：
- `generate_question(StudyMode.MIX)` は内部で6つの基本モードからランダム選択
  - OPEN_RANGE, THREE_BET, THREE_BET_DEFENCE, POWER_NUMBER, BB_DEFENCE, MDF_TRAINER
- UI上は "MIX（6モードランダム）" と表示されるが、実際の問題は個別モード
- `requested_mode` (UI選択) と `mode` (実際の問題) を分けて管理

### 3betモードのチェックボックス方式

他のモードと異なり、3betモードは **複数選択式**：
- HTML側: `<input type="checkbox" name="user_actions" value="3bet|call|fold">`
- サーバー側: `user_actions: List[str] = Form(None)` で受け取り
- 正解: `correct_action` はカンマ区切り文字列（例: `"3bet,call"`）
- 判定: セット比較 `user_set == expected_set`

### SB first-inモードの3択方式

オープンレンジモードでHeroがSBの場合のみ **3択（RAISE/LIMP/FOLD）**：
- HTML側: Hero positionが `SB` の場合のみ3択ボタンを表示
- サーバー側: `sb_first_in_action()` で判定
- ルール：
  1. BTNオープンレンジに入る → `"raise"`
  2. オフスート → `"fold"`
  3. スーテッドで下≤3 → `"fold"`
  4. 残りスーテッド（下≥4） → `"limp"`

### 不正解時のレンジ表示機能

`last_result` が存在し、かつ `not last_result.is_correct` の場合：
- **BB defence**: ポジション別CALLレンジの表を表示
- **SB first-in**: RAISE/LIMP/FOLDの説明リストを表示
- **その他モード**: 既存の説明ブロック（3bet、3betディフェンス、パワーナンバー）

条件分岐：
```jinja2
{% if last_result and not last_result.is_correct %}
    {% if last_result.mode == 'bb_defence' %}
        <!-- BB defence表 -->
    {% elif last_result.mode == 'open_range' and last_result.hero_pos == 'SB' %}
        <!-- SB first-in説明 -->
    {% elif last_result.mode == 'three_bet' %}
        <!-- 既存の3bet説明 -->
    ...
{% endif %}
```

---

## Claude に守ってほしい基本方針

1. **必ずこの `claude.md` を一度読んでから作業を始めること。**
2. 仕様変更と実装変更を混ぜない。  
   - 仕様（レンジの定義、ロジックのルール）が曖昧な場合は、  
     ユーザーのプロンプト（実装依頼メモ）を最優先する。
3. ユーザーのレンジ設計（簡易オープンレンジ、3betルール、PNルールなど）が  
   プロンプト内で明示されている場合、**その定義を真実として実装すること**。
4. 「勝手にレンジロジックを変えない」。  
   - 例：`in_open_range` などの関数の条件を、  
     ユーザー指定なしで独自に変えない。
5. 既存コードのスタイルを基本的に踏襲する。
   - 型ヒントはあれば合わせる程度（必須ではない）。
   - 読みやすさとシンプルさを優先。
6. 大きな変更をするときは、可能なら **ファイル全体を書き直す** 形で提案してよい。  
   ただし、用途が「トレーナーとしての挙動修正」だけで済むなら  
   **差分レベルの修正**で十分。

---

## 具体的な動作方針

### 1. 新しいレンジロジックを実装するとき

ユーザーから以下のような情報が与えられる想定：

- 新しいレンジ定義（例：4betレンジ、別スタックサイズのPNルールなど）
- どのモードに組み込みたいか
- 影響範囲（だいたい `core/ranges_*.py`, `quiz/generators.py`, `web/routes.py`, `templates/index.html`）

Claude のやること：

1. ユーザーが提示したロジック仕様を読み取る。
2. 既存のレンジ判定関数の構造を理解する。
3. **既存パターンに合わせて** 新しい関数 or 既存関数修正を行う：
   - `core/enums.py` に新しいStudyModeを追加（必要な場合）
   - `core/ranges_*.py` に判定ロジックを実装
   - `quiz/generators.py` に問題生成関数を追加
   - `web/routes.py` の `answer()` に回答判定を追加
4. 必要なら UI にモードの選択肢を追加し、問題テキストも調整する（`templates/index.html`）。

### 2. テンプレート（`index.html`）をいじるとき

- できるだけ
  - モバイルで見やすい
  - 情報が整理されていて、Hero のポジション・相手のポジション・ハンド・M値がパッと入る
- JS は必要最低限（Jinja と素の JS / DOM 操作で足りる範囲に収める）

**禁止事項**

- React や Vue などのフレームワーク導入
- 大量の外部CSSフレームワーク追加（Tailwind/Bootstrap等）  
  → このプロジェクトではシンプルさ優先。

---

## ユーザーからの実装依頼フォーマット（期待する形）

ユーザーは、実装を依頼するときに、`claude.md` を前提にして  
次のような形で指示する想定：

```markdown
### Task
- 新しい 4bet レンジモードを追加してほしい。
- 既存の 3bet ロジックは変えない。
- 「4bet するか / fold するか」のクイズモードを1つ追加したい。

### Logic Spec
- プリフロは 3bet が入っている前提。
- Hero の 4bet レンジは、ポジションごとに以下のルール：
  - UTG vs BTN 3bet: { …具体ルール… }
  - CO vs BTN 3bet: { … }
- UTG, CO, BTN 以外からの 4bet は今回対象外で OK。

### Files to Edit
- `core/enums.py`
  - `StudyMode` に `FOUR_BET` を追加
- `core/ranges_4bet.py`（新規作成）
  - 4bet 判定関数の実装
- `quiz/generators.py`
  - `generate_four_bet_question()` を追加
  - `generate_question()` に 4bet モードを追加
- `web/routes.py`
  - `answer()` に 4bet の回答判定を追加
- `templates/index.html`
  - モード選択プルダウンに「4betレンジ」を追加
  - 出題テンプレート内に「3betした相手ポジション」などの説明を追加

### Constraints
- 既存の OPEN_RANGE / 3BET / 3BET_DEFENCE / POWER_NUMBER / BB_DEFENCE / MDF_TRAINER の挙動は変えないこと。
- コードはなるべく既存スタイルに合わせること。
- 新しいレンジ判定は `core/ranges_4bet.py` として分離すること。
```

---

## 実装済み機能の詳細

### BB defence（CALLレンジ）モード

**目的**: BBでオープンに対してdefend(call)するかfoldするかを瞬時に判断

**実装場所**:
- [core/ranges_bb_defence.py](core/ranges_bb_defence.py) - `bb_defence_vs_open()` 関数
- [quiz/generators.py](quiz/generators.py) - `generate_bb_defence_question()` 関数
- [templates/index.html](templates/index.html) - UI（問題タイトル、DEFEND/FOLDボタン、不正解時のレンジ表）

**レンジ定義**:
- vs UTG: AQo+, ATs+, 両方≥11, コネ(下≥7 & gap≤1), 66+
- vs UTG+1/2: AJo+, 両方≥12, 全Axs, 両方≥10, コネ(下≥6 & gap≤1), 55+
- vs LJ/HJ: ATo+, 両方≥11, 全Axs, 両方≥8, コネ/ギャッパ(下≥4 & gap≤2), 22+
- vs CO/BTN: A8o+, 両方≥10, 全Axs, 両方≥7, コネ/ギャッパ(下≥4 & gap≤2), 22+

### SB first-in モード

**目的**: SB first-in（全員フォールド）でのRAISE/LIMP/FOLDの判断

**実装場所**:
- [core/ranges_sb_open.py](core/ranges_sb_open.py) - `sb_first_in_action()` 関数
- [quiz/generators.py](quiz/generators.py) - `generate_open_range_question()` にSB対応
- [templates/index.html](templates/index.html) - UI（SB時の3択ボタン、不正解時のレンジ説明）

**ルール**:
1. BTNオープンレンジに入る → RAISE
2. オフスート → FOLD
3. スーテッドで下≤3 → FOLD
4. 残りスーテッド（下≥4） → LIMP

**補足**: Limp pot後の対応はv2以降。暫定的に「UTG+1/2 openレンジを参考にdefence」で運用。

---

### MDF Trainer（Flop / v1）モード

**目的**: レンジ × フロップのバケット分布を理解し、MDFを満たすdefend範囲を学習

**実装場所**:
- [core/enums.py](core/enums.py) - `Card`型、`Bucket` Enum、`BUCKET_ORDER`
- [core/cards.py](core/cards.py) - カード・ボード生成、コンボ列挙ユーティリティ
- [core/range_combos.py](core/range_combos.py) - `get_range_combos()` レンジ→コンボセット変換
- [mdf/evaluator.py](mdf/evaluator.py) - `evaluate_hand_strength()` バケット分類
- [mdf/analysis.py](mdf/analysis.py) - `calculate_mdf_analysis()` MDF計算とカットオフ決定
- [quiz/generators.py](quiz/generators.py) - `generate_mdf_trainer_question()` 問題生成
- [templates/index.html](templates/index.html) - UI（MDF用スタイル、バケット選択、分析結果表示、10秒タイマー）

**データ構造**:
- カード表現: `Card = Tuple[int, str]` （例: `(14, 's')` = As）
- バケット順序（強→弱）:
  1. **Monster**: Set以上（two pair, straight, flush含む）
  2. **Strong Made**: Top pair 強キッカー（Q以上）
  3. **Weak Made**: Weak TP / 2nd-3rd pair / Over pair
  4. **Draw**: FD / OESD / GS
  5. **SD Value**: A-high / K-high（未ヒット）
  6. **Air**: それ以外

**判定ルール（Priority順）**:
- Priority 1 (Monster): フラッシュ/ストレート/セット/ツーペア判定
- Priority 2 (Strong Made): トップペア＆キッカー≥Q
- Priority 3 (Weak Made): トップペア（弱キッカー）/2nd-3rdペア/オーバーペア
- Priority 4 (Draw): FD（4枚同スート）/OESD/GS判定
- Priority 5 (SD Value): A-high / K-high
- Priority 6 (Air): 上記以外

**対応レンジ**:
- オープンレンジ: OPEN_UTG, OPEN_UTG1, OPEN_LJ, OPEN_HJ, OPEN_CO, OPEN_BTN
- 3BET_DEFENCE（UTG+1/2レンジ相当）
- BB_DEFENCE_vs_UTG / BB_DEFENCE_vs_CO / BB_DEFENCE_vs_BTN
- SB_RFI（SB first-inのRAISEレンジのみ）

**MDF計算フロー**:
1. レンジから全コンボを列挙（1326コンボ→レンジフィルタ）
2. ボードとカードが被るコンボを除外
3. 各コンボをバケット分類
4. MDF = 1 / (1 + bet_size) を計算
5. 強い順から累積し、need_defend = ceil(total_combos * MDF) を満たすバケットを特定
6. カットオフバケットの途中で跨ぐ場合、mix比率を計算

**UI/UX**:
- 問題: レンジ名、ボード3枚、Bet size（pot比）を表示
- 回答: 6つのバケットからラジオボタンで選択
- 結果: MDF / Total Combos / Need Defend / Cutoff を表示
- バケット表: Count / Pct / Cum count / Cum pct を一覧表示
- Mix必要時: 「Bucket X の上位 Y% をdefend（ランダムmix）」を表示

**v1の制約**:
- フロップのみ対応（ターン/リバーはv2以降）
- 相手レンジ・SPR・実戦略（CB頻度等）は考慮しない
- バケット定義は固定（GTO厳密性よりも学習の一貫性を優先）

**設計思想**:
- 数学的に厳密なGTO戦略ではなく、「レンジ×ボードの分布変化」と「MDFという制約」を体感させるトレーナー
- バケット定義の一貫性を最優先（実装者が迷わない明確なルール）
- 既存のレンジ判定関数を再利用してコード重複を最小化