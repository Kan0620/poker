# mdf/evaluator.py
from typing import List, Tuple
from collections import Counter
from core.enums import Card, Bucket


def evaluate_hand_strength(hand: Tuple[Card, Card], board: List[Card]) -> Bucket:
    """
    ハンド2枚 + ボード3枚 から、バケットを判定する。
    優先度順に判定し、最初に該当したものを返す。
    """
    c1, c2 = hand
    all_five = [c1, c2] + board

    # ランクとスートの抽出
    ranks = [c[0] for c in all_five]
    suits = [c[1] for c in all_five]
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)

    board_ranks = [c[0] for c in board]
    board_suits = [c[1] for c in board]
    hand_ranks = [c1[0], c2[0]]
    hand_suits = [c1[1], c2[1]]

    # ボードの最高ランク
    r_top = max(board_ranks)

    # ===== Priority 1: Monster =====
    # straight以上 OR two pair以上 OR set

    # フラッシュチェック（5枚中同スート5枚）
    for count in suit_counts.values():
        if count >= 5:
            return Bucket.MONSTER

    # ストレートチェック
    unique_ranks = sorted(set(ranks), reverse=True)
    # ホイール対応（A-2-3-4-5）
    if set([14, 5, 4, 3, 2]).issubset(set(unique_ranks)):
        return Bucket.MONSTER
    # 通常ストレート
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i+4] == 4:
            return Bucket.MONSTER

    # カウント系役
    pairs = [r for r, cnt in rank_counts.items() if cnt == 2]
    trips = [r for r, cnt in rank_counts.items() if cnt == 3]
    quads = [r for r, cnt in rank_counts.items() if cnt == 4]

    if quads:
        return Bucket.MONSTER
    if trips:
        # フルハウスまたはセット
        if len(pairs) > 0:
            # フルハウス
            return Bucket.MONSTER
        # セット（トリップス）
        # ポケットがボードにヒットした場合のみセット
        if hand_ranks[0] == hand_ranks[1] and hand_ranks[0] in trips:
            return Bucket.MONSTER
    if len(pairs) >= 2:
        # ツーペア
        # 両方がボードにヒットしたか確認
        hand_hit_count = sum(1 for hr in hand_ranks if hr in board_ranks)
        if hand_hit_count == 2:
            return Bucket.MONSTER

    # ===== Priority 2: Strong Made =====
    # トップペア＆キッカー強い（k >= Q）、オーバーペア
    for hr in hand_ranks:
        if hr == r_top:
            # トップペアを持っている
            kicker = [r for r in hand_ranks if r != hr][0] if hand_ranks[0] != hand_ranks[1] else hr
            if kicker >= 12:  # Q以上
                return Bucket.STRONG_MADE

    # オーバーペア（トップペアより強い）
    if hand_ranks[0] == hand_ranks[1]:
        pocket_rank = hand_ranks[0]
        if pocket_rank > r_top:
            return Bucket.STRONG_MADE

    # ===== Priority 3: Weak Made =====
    # トップペア（Strongでない）、2ndペア、3rdペア、ポケットペア（全て）

    # トップペア（キッカー弱い）
    for hr in hand_ranks:
        if hr == r_top:
            return Bucket.WEAK_MADE

    # ポケットペア（ボードに絡んでいるか関係なく全て）
    if hand_ranks[0] == hand_ranks[1]:
        return Bucket.WEAK_MADE

    # 2ndペア、3rdペア
    board_ranks_sorted = sorted(set(board_ranks), reverse=True)
    for hr in hand_ranks:
        if len(board_ranks_sorted) >= 2 and hr == board_ranks_sorted[1]:
            return Bucket.WEAK_MADE
        if len(board_ranks_sorted) >= 3 and hr == board_ranks_sorted[2]:
            return Bucket.WEAK_MADE

    # ===== Priority 4: Draw =====
    # FD, OESD, GS

    # フラッシュドロー（手札2枚同スート、ボードに同スート2枚）
    if hand_suits[0] == hand_suits[1]:
        hand_suit = hand_suits[0]
        board_suit_count = sum(1 for s in board_suits if s == hand_suit)
        if board_suit_count == 2:
            # 合計4枚同スート → FD
            return Bucket.DRAW

    # ストレートドロー（OESD, GS）
    unique_5 = sorted(set(ranks), reverse=True)
    # ホイール系も考慮
    if 14 in unique_5:
        unique_5_with_low_ace = unique_5 + [1]
    else:
        unique_5_with_low_ace = unique_5

    # 4連続チェック（OESDまたはGS）
    for i in range(len(unique_5_with_low_ace) - 3):
        four = [unique_5_with_low_ace[i + j] for j in range(4)]
        if max(four) - min(four) == 3:
            # 4連続が揃っている（gap=0 → OESD確定）
            return Bucket.DRAW
        elif max(four) - min(four) == 4:
            # 5ランクに4枚 → gap=1 → ガットショット
            return Bucket.DRAW

    # ===== Priority 5: SD Value =====
    # A-high / K-high（未ヒット、かつDrawではない）

    high_card = max(hand_ranks)
    if high_card == 14:  # A-high
        return Bucket.SD_VALUE
    if high_card == 13:  # K-high
        return Bucket.SD_VALUE

    # ===== Priority 6: Air =====
    return Bucket.AIR
