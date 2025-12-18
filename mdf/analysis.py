# mdf/analysis.py
import math
from typing import Dict, Any, Set, Tuple, List
from core.enums import Card, Bucket, BUCKET_ORDER
from core.cards import blocks_with_board, card_to_str
from mdf.evaluator import evaluate_hand_strength


def calculate_mdf_analysis(range_combos: Set[Tuple[Card, Card]], board: List[Card], bet_size: float) -> Dict[str, Any]:
    """
    レンジ × ボード から、バケット分布、MDF、カットオフを計算する。

    Returns:
        {
            'mdf': float,
            'total_combos': int,
            'need_defend_combos': int,
            'cutoff_bucket': str,
            'mix_required': bool,
            'mix_ratio': float or None,
            'buckets': [
                {
                    'name': str,
                    'count': int,
                    'pct': float,
                    'cum_count': int,
                    'cum_pct': float
                },
                ...
            ]
        }
    """
    # ボードと被るコンボを除外
    valid_combos = [c for c in range_combos if not blocks_with_board(c, board)]
    total_combos = len(valid_combos)

    if total_combos == 0:
        # ボードがレンジを全部ブロックしてしまう稀なケース
        return {
            'mdf': 0.0,
            'total_combos': 0,
            'need_defend_combos': 0,
            'cutoff_bucket': 'N/A',
            'mix_required': False,
            'mix_ratio': None,
            'buckets': []
        }

    # MDF計算
    mdf = 1.0 / (1.0 + bet_size)
    need_defend = math.ceil(total_combos * mdf)

    # バケット分類
    bucket_combos: Dict[Bucket, List] = {b: [] for b in BUCKET_ORDER}
    for combo in valid_combos:
        bucket = evaluate_hand_strength(combo, board)
        bucket_combos[bucket].append(combo)

    # バケット集計（強い順）
    bucket_list = []
    cum_count = 0
    prev_cum = 0
    cutoff_bucket = None
    mix_required = False
    mix_ratio = None

    for bucket in BUCKET_ORDER:
        count = len(bucket_combos[bucket])
        pct = (count / total_combos * 100) if total_combos > 0 else 0.0
        cum_count += count
        cum_pct = (cum_count / total_combos * 100) if total_combos > 0 else 0.0

        bucket_data = {
            'name': bucket.value,
            'count': count,
            'pct': round(pct, 1),
            'cum_count': cum_count,
            'cum_pct': round(cum_pct, 1)
        }

        # 常にハンド一覧を生成（トグル表示用）
        if count > 0:
            hands = []
            for combo in bucket_combos[bucket]:
                c1, c2 = combo
                hand_str = f"{card_to_str(c1)}{card_to_str(c2)}"
                hands.append(hand_str)
            bucket_data['hands'] = hands

        bucket_list.append(bucket_data)

        # カットオフ判定
        if cutoff_bucket is None:
            if cum_count >= need_defend:
                cutoff_bucket = bucket.value
                # mix判定
                if prev_cum < need_defend < cum_count:
                    mix_required = True
                    need_in_bucket = need_defend - prev_cum
                    mix_ratio = round((need_in_bucket / count * 100), 1) if count > 0 else 0.0

        prev_cum = cum_count

    # カットオフが見つからない場合（全コンボでも足りない）
    if cutoff_bucket is None:
        cutoff_bucket = Bucket.AIR.value

    return {
        'mdf': round(mdf, 3),
        'total_combos': total_combos,
        'need_defend_combos': need_defend,
        'cutoff_bucket': cutoff_bucket,
        'mix_required': mix_required,
        'mix_ratio': mix_ratio,
        'buckets': bucket_list
    }
