# quiz/generators.py
import random
from typing import Dict, Any
from core.enums import StudyMode, Position, POSITIONS
from core.utils_hand import random_hand, hand_label
from core.ranges_open import in_open_range
from core.ranges_3bet import three_bet_allowed_actions
from core.ranges_3bet_defence import three_bet_defence_action
from core.ranges_bb_defence import bb_defence_vs_open
from core.ranges_sb_open import sb_first_in_action
from core.power_number import should_shove_with_power_number
from core.cards import generate_board, card_to_str
from core.range_combos import get_range_combos
from mdf.analysis import calculate_mdf_analysis


def generate_open_range_question() -> Dict[str, Any]:
    # SBを除外（SB_OPENモードで別途扱う）
    hero_pos = random.choice(POSITIONS)
    hi, lo, suited = random_hand()
    label = hand_label(hi, lo, suited)

    correct = "open" if in_open_range(hero_pos, hi, lo, suited) else "fold"

    return {
        "mode": StudyMode.OPEN_RANGE.value,
        "hero_pos": hero_pos.value,
        "villain_pos": "",
        "hand_hi": hi,
        "hand_lo": lo,
        "suited": suited,
        "hand_label": label,
        "m_value": None,
        "in_position": None,
        "correct_action": correct,
    }


def generate_sb_open_question() -> Dict[str, Any]:
    """SB first-in専用の問題生成（raise/limp/fold の3択）"""
    hi, lo, suited = random_hand()
    label = hand_label(hi, lo, suited)

    correct = sb_first_in_action(hi, lo, suited)

    return {
        "mode": StudyMode.SB_OPEN.value,
        "hero_pos": Position.SB.value,
        "villain_pos": "",
        "hand_hi": hi,
        "hand_lo": lo,
        "suited": suited,
        "hand_label": label,
        "m_value": None,
        "in_position": None,
        "correct_action": correct,
    }


def generate_three_bet_question() -> Dict[str, Any]:
    # VillainポジションをBTN以外（UTG〜CO）からランダムに選択
    # POSITIONS = [UTG, UTG+1, UTG+2, LJ, HJ, CO, BTN]
    # インデックス 0〜5 がBTN以外
    villain_positions = POSITIONS[:-1]  # BTNを除外
    villain_pos = random.choice(villain_positions)

    # Heroポジションは Villainより後ろのポジションからランダムに選ぶ
    villain_idx = POSITIONS.index(villain_pos)
    # villain_idx + 1 から最後まで（BTN含む）
    hero_positions = POSITIONS[villain_idx + 1:]
    hero_pos = random.choice(hero_positions)

    hi, lo, suited = random_hand()
    label = hand_label(hi, lo, suited)
    allowed = three_bet_allowed_actions(hero_pos, villain_pos, hi, lo, suited)

    correct_action = ",".join(sorted(allowed))  # "3bet,call" など

    return {
        "mode": StudyMode.THREE_BET.value,
        "hero_pos": hero_pos.value,
        "villain_pos": villain_pos.value,
        "hand_hi": hi,
        "hand_lo": lo,
        "suited": suited,
        "hand_label": label,
        "m_value": None,
        "in_position": None,
        "correct_action": correct_action,
    }


def generate_three_bet_defence_question() -> Dict[str, Any]:
    # Heroは常にオープナー。UTG〜BTN からランダムで選ぶ
    hero_pos = random.choice(POSITIONS)

    # Heroのオープンレンジ内からハンドをサンプル
    while True:
        hi, lo, suited = random_hand()
        if in_open_range(hero_pos, hi, lo, suited):
            break

    # BTNだけは SB / BB から3betされるケースを明示的に作る（HeroはIP）
    if hero_pos == Position.BTN:
        villain_pos = random.choice([Position.SB, Position.BB])
        in_pos = True
    else:
        # それ以外は「自分より後ろのポジション」から3betされる前提（HeroはOOP）
        hero_idx = POSITIONS.index(hero_pos)
        v_idx = random.randint(hero_idx + 1, len(POSITIONS) - 1)
        villain_pos = POSITIONS[v_idx]
        in_pos = False

    label = hand_label(hi, lo, suited)
    action = three_bet_defence_action(hero_pos, in_pos, hi, lo, suited)

    return {
        "mode": StudyMode.THREE_BET_DEFENCE.value,
        "hero_pos": hero_pos.value,
        "villain_pos": villain_pos.value,
        "hand_hi": hi,
        "hand_lo": lo,
        "suited": suited,
        "hand_label": label,
        "m_value": None,
        "in_position": in_pos,
        "correct_action": action,  # "defend" or "fold"
    }


def generate_power_number_question() -> Dict[str, Any]:
    hero_pos = random.choice(POSITIONS)
    # M値は 1.0〜5.5 のどこか
    m_value = round(random.uniform(1.0, 5.5), 1)

    hi, lo, suited = random_hand()
    label = hand_label(hi, lo, suited)

    shove = should_shove_with_power_number(hero_pos, hi, lo, suited, m_value)
    correct = "shove" if shove else "fold"

    return {
        "mode": StudyMode.POWER_NUMBER.value,
        "hero_pos": hero_pos.value,
        "villain_pos": "",
        "hand_hi": hi,
        "hand_lo": lo,
        "suited": suited,
        "hand_label": label,
        "m_value": m_value,
        "in_position": None,
        "correct_action": correct,
    }


def generate_bb_defence_question() -> Dict[str, Any]:
    # VillainポジションはUTG〜BTN（BBを除く）からランダムに選択
    villain_positions = [
        Position.UTG,
        Position.UTG1,
        Position.UTG2,
        Position.LJ,
        Position.HJ,
        Position.CO,
        Position.BTN,
    ]
    villain_pos = random.choice(villain_positions)

    hi, lo, suited = random_hand()
    label = hand_label(hi, lo, suited)

    defend = bb_defence_vs_open(villain_pos, hi, lo, suited)
    correct = "defend" if defend else "fold"

    return {
        "mode": StudyMode.BB_DEFENCE.value,
        "hero_pos": Position.BB.value,
        "villain_pos": villain_pos.value,
        "hand_hi": hi,
        "hand_lo": lo,
        "suited": suited,
        "hand_label": label,
        "m_value": None,
        "in_position": None,
        "correct_action": correct,
    }


def generate_mdf_trainer_question() -> Dict[str, Any]:
    """
    MDF Trainerモードの問題を生成する。
    1. ランダムにレンジを選択
    2. ボードを生成
    3. bet sizeをランダムに選択
    4. MDF計算を実行
    5. 正解はcutoff_bucket
    """
    # レンジ候補（仕様に沿った候補）
    range_options = [
        "OPEN_UTG",
        "OPEN_UTG1",
        "OPEN_LJ",
        "OPEN_HJ",
        "OPEN_CO",
        "OPEN_BTN",
        "3BET_DEFENCE_IP",
        "3BET_DEFENCE_OOP",
        "BB_DEFENCE_vs_UTG",
        "BB_DEFENCE_vs_CO",
        "BB_DEFENCE_vs_BTN",
        "SB_RFI",
    ]
    range_name = random.choice(range_options)

    # ボード生成
    board = generate_board()
    board_display = [card_to_str(c) for c in board]  # 表示用（絵文字）
    board_raw = [f"{c[0]}{c[1]}" for c in board]  # hidden field用（数値形式）

    # bet size候補（v1仕様）
    bet_sizes = [0.25, 0.33, 0.50, 0.80, 1.25]
    bet_size = random.choice(bet_sizes)

    # レンジコンボ取得
    range_combos = get_range_combos(range_name)

    # MDF分析実行
    analysis = calculate_mdf_analysis(range_combos, board, bet_size)

    # 正解はcutoff_bucket
    correct_bucket = analysis['cutoff_bucket']

    return {
        "mode": StudyMode.MDF_TRAINER.value,
        "range_name": range_name,
        "board": board_display,  # 表示用
        "board_raw": ",".join(board_raw),  # hidden field用（カンマ区切り）
        "bet_size": bet_size,
        "correct_action": correct_bucket,  # 正解バケット
        "analysis": analysis,  # 答え合わせ用データ
        # 既存フォーマットとの互換性のため
        "hero_pos": "",
        "villain_pos": "",
        "hand_hi": 0,
        "hand_lo": 0,
        "suited": False,
        "hand_label": "",
        "m_value": None,
        "in_position": None,
    }


def generate_question(mode: StudyMode) -> Dict[str, Any]:
    if mode == StudyMode.OPEN_RANGE:
        return generate_open_range_question()
    elif mode == StudyMode.SB_OPEN:
        return generate_sb_open_question()
    elif mode == StudyMode.THREE_BET:
        return generate_three_bet_question()
    elif mode == StudyMode.THREE_BET_DEFENCE:
        return generate_three_bet_defence_question()
    elif mode == StudyMode.POWER_NUMBER:
        return generate_power_number_question()
    elif mode == StudyMode.BB_DEFENCE:
        return generate_bb_defence_question()
    elif mode == StudyMode.MDF_TRAINER:
        return generate_mdf_trainer_question()
    else:
        # MIX の時は7モードからランダム（SB_OPEN, MDF_TRAINER含む）
        base_mode = random.choice([
            StudyMode.OPEN_RANGE,
            StudyMode.SB_OPEN,
            StudyMode.THREE_BET,
            StudyMode.THREE_BET_DEFENCE,
            StudyMode.POWER_NUMBER,
            StudyMode.BB_DEFENCE,
            StudyMode.MDF_TRAINER,
        ])
        return generate_question(base_mode)
