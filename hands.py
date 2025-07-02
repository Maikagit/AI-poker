from itertools import combinations

RANK_ORDER = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':11,'Q':12,'K':13,'A':14}

HAND_RANKS = [
    "High Card",
    "Pair",
    "Two Pair",
    "Three of a Kind",
    "Straight",
    "Flush",
    "Full House",
    "Four of a Kind",
    "Straight Flush",
]


def card_value(card):
    return RANK_ORDER[card.rank]


def is_flush(cards):
    suit = cards[0].suit
    return all(c.suit == suit for c in cards)


def is_straight(cards):
    values = sorted([card_value(c) for c in cards])
    for i in range(1, len(values)):
        if values[i] != values[i-1] + 1:
            return False
    return True


def evaluate_five(cards):
    values = sorted([card_value(c) for c in cards], reverse=True)
    counts = {v: values.count(v) for v in set(values)}
    is_flush_hand = is_flush(cards)
    is_straight_hand = is_straight(cards)

    if is_straight_hand and is_flush_hand:
        return (8, [max(values)])
    if 4 in counts.values():
        four = [v for v in counts if counts[v] == 4][0]
        kicker = max(v for v in values if v != four)
        return (7, [four, kicker])
    if sorted(counts.values()) == [2,3]:
        three = [v for v in counts if counts[v] == 3][0]
        pair = [v for v in counts if counts[v] == 2][0]
        return (6, [three, pair])
    if is_flush_hand:
        return (5, values)
    if is_straight_hand:
        return (4, [max(values)])
    if 3 in counts.values():
        three = [v for v in counts if counts[v] == 3][0]
        kickers = sorted([v for v in values if v != three], reverse=True)
        return (3, [three] + kickers)
    if list(counts.values()).count(2) == 2:
        pairs = sorted([v for v in counts if counts[v] == 2], reverse=True)
        kicker = max(v for v in values if v not in pairs)
        return (2, pairs + [kicker])
    if 2 in counts.values():
        pair = [v for v in counts if counts[v] == 2][0]
        kickers = sorted([v for v in values if v != pair], reverse=True)
        return (1, [pair] + kickers)
    return (0, values)


def evaluate_seven(cards):
    best = (-1, [])
    for combo in combinations(cards, 5):
        rank = evaluate_five(list(combo))
        if rank > best:
            best = rank
    return best
