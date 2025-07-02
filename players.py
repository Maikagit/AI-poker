import random
from hands import evaluate_seven, HAND_RANKS


class Player:
    def __init__(self, name, chips=1000, is_human=False):
        self.name = name
        self.chips = chips
        self.cards = []
        self.bet = 0
        self.folded = False
        self.is_human = is_human

    def reset_for_round(self):
        self.cards = []
        self.bet = 0
        self.folded = False

    def hand_strength(self, community):
        return evaluate_seven(self.cards + community)

    def __str__(self):
        return f"{self.name} ({self.chips})"


class AIPlayer(Player):
    def decide(self, game, min_call):
        if self.folded:
            return 'fold'
        strength, _ = self.hand_strength(game.community)
        # very naive strategy
        if strength >= 2:  # at least two pair
            if min_call > self.chips:
                return 'fold'
            if random.random() < 0.5:
                return 'raise'
            return 'call'
        if strength == 1 and min_call == 0:
            return 'bet'
        if min_call <= game.big_blind:
            return 'call'
        return 'fold'
