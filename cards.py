class Card:
    SUITS = ['coeur', 'carreau', 'trefle', 'pique']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self, rank, suit, image_path=None):
        self.rank = rank
        self.suit = suit
        self.image_path = image_path

    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 11 + ['J', 'Q', 'K'].index(self.rank)
        if self.rank == 'A':
            return 14
        return int(self.rank)

    def __repr__(self):
        return f"{self.rank} de {self.suit}"


class Deck:
    def __init__(self, templates_dir='card_templates'):
        self.cards = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                image_name = f"{rank}_{suit}.png"
                image_path = f"{templates_dir}/{image_name}"
                self.cards.append(Card(rank, suit, image_path))
        self.position = 0

    def shuffle(self):
        import random
        random.shuffle(self.cards)
        self.position = 0

    def deal(self, n=1):
        dealt = self.cards[self.position:self.position + n]
        self.position += n
        return dealt
