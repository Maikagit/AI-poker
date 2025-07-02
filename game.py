import pygame
from collections import deque
from cards import Deck
from players import Player, AIPlayer
from hands import HAND_RANKS

class PokerGame:
    def __init__(self, human_name='Vous', nb_ai=2, templates='card_templates', width=1024, height=768):
        self.deck = Deck(templates)
        self.players = [Player(human_name, is_human=True)]
        self.players += [AIPlayer(f"IA{i+1}") for i in range(nb_ai)]
        self.community = []
        self.small_blind = 10
        self.big_blind = 20
        self.current_bet = 0
        self.pot = 0
        self.dealer = 0
        self.history = deque()
        self.width = width
        self.height = height

        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.card_back = pygame.image.load(f"{templates}/dos.png")
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Texas Holdem')

    def rotate_dealer(self):
        self.dealer = (self.dealer + 1) % len(self.players)

    def deal_new_round(self):
        self.deck.shuffle()
        self.community = []
        for p in self.players:
            p.reset_for_round()
            p.cards = self.deck.deal(2)
        self.current_bet = 0
        self.pot = 0

    def betting_round(self, start_index):
        idx = start_index
        players_in = [p for p in self.players if not p.folded and p.chips > 0]
        last_raiser = None
        while True:
            player = self.players[idx]
            if not player.folded and player.chips > 0:
                to_call = self.current_bet - player.bet
                action = None
                if player.is_human:
                    action = self.human_decide(player, to_call)
                else:
                    action = player.decide(self, to_call)
                if action == 'fold':
                    player.folded = True
                elif action in ['call', 'bet', 'raise']:
                    bet_amount = 0
                    if action == 'call':
                        bet_amount = to_call
                    elif action == 'bet':
                        bet_amount = self.big_blind
                        self.current_bet = bet_amount
                    elif action == 'raise':
                        bet_amount = to_call + self.big_blind
                        self.current_bet += self.big_blind
                    player.bet += bet_amount
                    player.chips -= bet_amount
                    self.pot += bet_amount
                    last_raiser = idx if action in ['bet','raise'] else last_raiser

                if not player.is_human:
                    self.draw()
                    msg = f"{player.name} {action}"
                    text = self.font.render(msg, True, (255,255,0))
                    self.screen.blit(text, (20, 20))
                    pygame.display.flip()
                    pygame.time.wait(2000)
                # check if betting is over
                if last_raiser is None:
                    if idx == (start_index - 1) % len(self.players):
                        break
                else:
                    if idx == last_raiser and all(p.bet == self.current_bet or p.folded for p in self.players):
                        break
            idx = (idx + 1) % len(self.players)
        for p in self.players:
            self.current_bet = 0
            p.bet = 0

    def human_decide(self, player, to_call):
        waiting = True
        action = 'fold'
        while waiting:
            self.draw()
            prompt = f"Votre tour: (c)all {to_call}, (r)aise, (f)old"
            text = self.font.render(prompt, True, (255,0,0))
            self.screen.blit(text, (10, self.height - 40))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        action = 'call'
                        waiting = False
                    elif event.key == pygame.K_r:
                        action = 'raise'
                        waiting = False
                    elif event.key == pygame.K_f:
                        action = 'fold'
                        waiting = False
        return action

    def showdown(self):
        active = [p for p in self.players if not p.folded]
        scores = [(p, p.hand_strength(self.community)) for p in active]
        winner_player, rank = max(scores, key=lambda s: s[1])
        winner_player.chips += self.pot
        desc = HAND_RANKS[rank[0]]
        self.history.append(f"{winner_player.name}: {desc}")
        return winner_player, desc

    def draw(self):
        self.screen.fill((0,128,0))
        # community cards
        x = self.width//2 - 160
        y = self.height//2 - 100
        for card in self.community:
            img = pygame.image.load(card.image_path)
            self.screen.blit(img, (x,y))
            x += 80
        # players
        positions = [
            (50, self.height - 200),
            (self.width - 200, self.height - 200),
            (self.width // 2 - 100, 50),
        ]
        for i, player in enumerate(self.players):
            px, py = positions[i]
            if player.is_human or not player.folded:
                for j, c in enumerate(player.cards):
                    img = pygame.image.load(c.image_path if (player.is_human or len(self.community)==5) else f"card_templates/dos.png")
                    self.screen.blit(img, (px + j*40, py))
            label = f"{player.name} - {player.chips}"
            text = self.font.render(label, True, (255,255,255))
            self.screen.blit(text, (px, py-20))
        pot_text = self.font.render(f"Pot: {self.pot}", True, (255,255,0))
        self.screen.blit(pot_text, (self.width//2 - 40, self.height//2 - 150))

        # history of last hands
        for i, entry in enumerate(list(self.history)[-5:][::-1]):
            hist_text = self.font.render(entry, True, (255,255,255))
            self.screen.blit(hist_text, (self.width - 250, 100 + i*20))

    def play_hand(self):
        self.deal_new_round()
        self.betting_round((self.dealer+1)%len(self.players))
        if self.active_players()<=1:
            return
        self.community += self.deck.deal(3)
        self.betting_round((self.dealer+1)%len(self.players))
        if self.active_players()<=1:
            return
        self.community += self.deck.deal(1)
        self.betting_round((self.dealer+1)%len(self.players))
        if self.active_players()<=1:
            return
        self.community += self.deck.deal(1)
        self.betting_round((self.dealer+1)%len(self.players))
        winner, desc = self.showdown()
        self.draw()
        text = self.font.render(f"{winner.name} gagne le pot ({desc})!", True, (255,255,0))
        self.screen.blit(text, (300, 300))
        pygame.display.flip()
        pygame.time.wait(3000)

    def active_players(self):
        return sum(1 for p in self.players if not p.folded and p.chips>0)

    def run(self):
        while True:
            self.play_hand()
            self.rotate_dealer()
            self.community = []
            for p in self.players:
                if p.chips <=0:
                    print(f"{p.name} est éliminé")
            if sum(p.chips>0 for p in self.players if p.is_human)==0:
                break
        pygame.quit()

if __name__ == '__main__':
    game = PokerGame()
    game.run()
