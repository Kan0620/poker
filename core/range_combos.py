# core/range_combos.py
from typing import Set, Tuple
from core.enums import Card, Position
from core.cards import enumerate_all_combos, combo_to_hand_type
from core.ranges_open import in_open_range
from core.ranges_3bet_defence import is_in_utg12_defence_core, defend_vs_ip_3bet
from core.ranges_bb_defence import bb_defence_vs_open
from core.ranges_sb_open import sb_first_in_action
from core.ranges_open import in_utg12_open_range


def get_range_combos(range_name: str) -> Set[Tuple[Card, Card]]:
    """
    指定されたレンジ名に対応する全コンボを返す。
    レンジ名の例: "OPEN_UTG", "OPEN_CO", "3BET_DEFENCE", "BB_DEFENCE_vs_CO", "SB_RFI"
    """
    all_combos = enumerate_all_combos()
    result = set()

    # オープンレンジ
    if range_name.startswith("OPEN_"):
        pos_str = range_name.replace("OPEN_", "")
        if pos_str == "UTG":
            pos = Position.UTG
        elif pos_str in ("UTG1", "UTG+1"):
            pos = Position.UTG1
        elif pos_str in ("UTG2", "UTG+2"):
            pos = Position.UTG2
        elif pos_str == "LJ":
            pos = Position.LJ
        elif pos_str == "HJ":
            pos = Position.HJ
        elif pos_str == "CO":
            pos = Position.CO
        elif pos_str == "BTN":
            pos = Position.BTN
        else:
            return result

        for combo in all_combos:
            hi, lo, suited = combo_to_hand_type(combo[0], combo[1])
            if in_open_range(pos, hi, lo, suited):
                result.add(combo)

    # 3bet defence IP（自分がIP、相手がOOPから3bet）
    elif range_name == "3BET_DEFENCE_IP":
        for combo in all_combos:
            hi, lo, suited = combo_to_hand_type(combo[0], combo[1])
            # IPの時はUTG+1/2レンジ全体をdefend
            if in_utg12_open_range(hi, lo, suited):
                result.add(combo)

    # 3bet defence OOP（自分がOOP、相手がIPから3bet）
    elif range_name == "3BET_DEFENCE_OOP":
        for combo in all_combos:
            hi, lo, suited = combo_to_hand_type(combo[0], combo[1])
            # OOPの時はタイトに: UTG+1/2レンジ内でさらにdefend_vs_ip_3betを満たすもの
            if is_in_utg12_defence_core(hi, lo, suited) and defend_vs_ip_3bet(hi, lo, suited):
                result.add(combo)

    # BB defence（ポジション別）
    elif range_name.startswith("BB_DEFENCE_vs_"):
        villain_str = range_name.replace("BB_DEFENCE_vs_", "")
        villain_pos = None
        if villain_str == "UTG":
            villain_pos = Position.UTG
        elif villain_str in ("UTG1", "UTG2"):
            villain_pos = Position.UTG1
        elif villain_str in ("LJ", "HJ"):
            villain_pos = Position.LJ
        elif villain_str == "CO":
            villain_pos = Position.CO
        elif villain_str == "BTN":
            villain_pos = Position.BTN

        if villain_pos:
            for combo in all_combos:
                hi, lo, suited = combo_to_hand_type(combo[0], combo[1])
                if bb_defence_vs_open(villain_pos, hi, lo, suited):
                    result.add(combo)

    # SB first-in（RFIのみ、limpは除く）
    elif range_name == "SB_RFI":
        for combo in all_combos:
            hi, lo, suited = combo_to_hand_type(combo[0], combo[1])
            if sb_first_in_action(hi, lo, suited) == "raise":
                result.add(combo)

    return result
