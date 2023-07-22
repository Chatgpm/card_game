import random

class Group:
    DANCER = 1
    DIVINER = 2
    ARTISAN = 3
    BUTCHER = 4
    PAINTER = 5
    MONK = 10


def draw_random():
    return random.choice([Group.DANCER,
                            Group.DIVINER,
                            Group.ARTISAN,
                            Group.BUTCHER,
                            Group.PAINTER,
                            Group.MONK])


class Strategy:
    RANDOM = 0
    MIN = 1
    MAX = 2
    MONK_MIN = 3
    MONK_MAX = 4


class Winner:
    A =  -1
    B = 1
    Tie = 0


class Player:

    mayor: int = 0

    def __init__(self, strategy=Strategy.RANDOM):
        self.cards = []
        self.supporters = []
        self.opponents = []
        self.strategy = strategy

    def set_mayor(self):
        if len(self.cards) == 1:
            self.mayor = self.cards[0]
            return
        if self.strategy == Strategy.RANDOM:
            self.mayor = random.choice(self.cards)
        elif self.strategy == Strategy.MIN:
            self.mayor = min(self.cards)
        elif self.strategy == Strategy.MAX:
            monk_excluded = [x for x in self.cards if x != Group.MONK]
            if len(monk_excluded) == 0:
                self.mayor = Group.MONK
            else:
                self.mayor = max(monk_excluded)
        elif self.strategy == Strategy.MONK_MIN:
            if Group.MONK in self.cards:
                self.mayor = Group.MONK
            else:
                self.mayor = min(self.cards)
        elif self.strategy == Strategy.MONK_MAX:
            self.mayor = max(self.cards)
        else:
            print("Setting Mayer failed. With Strategy: " + str(self.strategy))

    def draw_debate(self):
        debate_cards = self.cards[:]
        debate_cards.remove(self.mayor)
        to_draw = random.choice(debate_cards)
        self.cards.remove(to_draw)
        return to_draw


class Game:

    player_A: Player
    player_B: Player

    def __init__(self):
        self.neutral_zone = []

    def set_player(self, player_a, player_b):
        self.player_A = player_a
        self.player_B = player_b

    def draw_cards(self, num_draws):
        for _ in range(num_draws):
            self.player_A.cards.append(draw_random())
            self.player_B.cards.append(draw_random())

    def process_matching_cards(self, cards_a, cards_b):
        unique_cards_a = set(cards_a)
        unique_cards_b = set(cards_b)

        for card in unique_cards_a.intersection(unique_cards_b):
            count_a = cards_a.count(card)
            count_b = cards_b.count(card)

            if count_a > count_b:
                for _ in range(count_b):
                    cards_a.remove(card)
                    cards_b.remove(card)
                    self.neutral_zone.append(card)
            else:
                for _ in range(count_a):
                    cards_a.remove(card)
                    cards_b.remove(card)
                    self.neutral_zone.append(card)

    def debate(self):
        draw_a = self.player_A.draw_debate()
        draw_b = self.player_B.draw_debate()
        if draw_a - draw_b == 1:
            self.player_A.supporters.append(draw_a)
            self.player_A.supporters.append(draw_b)
        elif draw_b - draw_a == 1:
            self.player_B.supporters.append(draw_a)
            self.player_B.supporters.append(draw_b)
        elif draw_a == Group.MONK or draw_b == Group.MONK:
            self.player_A.supporters.append(draw_b)
            self.player_B.supporters.append(draw_a)
        else:
            self.player_A.supporters.append(draw_a)
            self.player_B.supporters.append(draw_b)

    def check_next_round(self):
        if len(self.player_A.cards) == 1:
            print("Player A has only one card left. Proceeding to the next round.")
            return True
        elif len(self.player_B.cards) == 1:
            print("Player B has only one card left. Proceeding to the next round.")
            return True
        return False

    def check_draw(self):
        if len(self.player_A.cards) == 0 and len(self.player_B.cards) == 0:
            print("The game results in a draw!")
            return True
        return False

    def shuffle_supporters(self, pool):
        print(f"player A mayor: {self.player_A.mayor}")
        print(f"player B mayor: {self.player_B.mayor}")
        supporters_a = [x for x in pool if (x == self.player_A.mayor or
                                        (x == self.player_A.mayor - 1 and x != self.player_B.mayor) or
                                            x == self.player_B.mayor + 1)]
        supporters_b = [x for x in pool if (x == self.player_B.mayor or
                                        (x == self.player_B.mayor - 1 and x != self.player_A.mayor) or
                                            x == self.player_A.mayor + 1)]
        return supporters_a, supporters_b

    def process_neutral_zone(self):
        if self.player_A.mayor == self.player_B.mayor:
            self.neutral_zone = [x for x in self.neutral_zone if x != self.player_A.mayor]

        if self.player_A.mayor == Group.MONK:
            monks = [x for x in self.neutral_zone if x == Group.MONK]
            self.player_B.supporters += monks

        if self.player_B.mayor == Group.MONK:
            monks = [x for x in self.neutral_zone if x == Group.MONK]
            self.player_A.supporters += monks

        supporters_a, supporters_b = self.shuffle_supporters(self.neutral_zone)

        self.player_A.supporters += supporters_a
        self.player_B.supporters += supporters_b

        self.neutral_zone = [x for x in self.neutral_zone if (x not in supporters_a and x not in supporters_b)]

    def process_supporters(self):
        supporters = self.player_A.supporters + self.player_B.supporters
        self.process_matching_cards(self.player_A.supporters, self.player_B.supporters)
        print(f"Processing supporters: {supporters}")
        supporters_a, supporters_b = self.shuffle_supporters(supporters)
        print(f"A: {supporters_a}, B: {supporters_b}")
        self.player_A.supporters += list(set(supporters_a))
        self.player_B.supporters += list(set(supporters_b))
        for s in (list(set(supporters_a)) + list(set(supporters_b))):
            supporters.remove(s)
        self.neutral_zone += supporters

    def process_monks(self):
        if self.player_A.mayor == Group.MONK and self.player_B.mayor == Group.MONK:
            return
        if self.player_A.mayor == Group.MONK:
            self.player_A.supporters += self.neutral_zone
            self.neutral_zone.clear()
        elif self.player_B.mayor == Group.MONK:
            self.player_B.supporters += self.neutral_zone
            self.neutral_zone.clear()
        elif Group.MONK in self.player_A.supporters and Group.MONK in self.player_B.supporters:
            monks_a = self.player_A.cards.count(Group.MONK)
            monks_b = self.player_B.cards.count(Group.MONK)
            if monks_a == monks_b:
                return
            if monks_a > monks_b:
                to_draw = random.choice(self.neutral_zone)
                self.neutral_zone.remove(to_draw)
                self.player_A.supporters.append(to_draw)
            else:
                to_draw = random.choice(self.neutral_zone)
                self.neutral_zone.remove(to_draw)
                self.player_B.supporters.append(to_draw)
        elif Group.MONK in self.player_A.supporters:
            self.player_A.supporters += self.neutral_zone
            self.neutral_zone.clear()
        elif Group.MONK in self.player_B.supporters:
            self.player_B.supporters += self.neutral_zone
            self.neutral_zone.clear()

    def first_round(self, num_draws):
        self.draw_cards(num_draws)
        print(f"Player A cards: {self.player_A.cards}")
        print(f"Player B cards: {self.player_B.cards}")

        self.process_matching_cards(self.player_A.cards, self.player_B.cards)
        print(f"Neutral Zone: {self.neutral_zone}")

        if self.check_draw():
            return False

        # Determine mayor
        self.player_A.set_mayor()
        print(f"player A mayor: {self.player_A.mayor}")
        self.player_B.set_mayor()
        print(f"player B mayor: {self.player_B.mayor}")

        # First round: the Public Debate
        while True:
            if self.check_next_round():
                break
            print(f"player_A has a group of {len(self.player_A.cards)}")
            print(f"player_B has a group of {len(self.player_B.cards)}")
            self.debate()
        return True

    def second_round(self, num_draws):
        cards_a = []
        cards_b = []
        for _ in range(num_draws):
            cards_a.append(draw_random())
            cards_b.append(draw_random())
        self.player_A.supporters += cards_a
        self.player_B.supporters += cards_b

    def third_round(self):
        self.process_neutral_zone()
        self.process_supporters()
        self.process_monks()

    def winner(self):
        print(f"player_A has a group of {len(self.player_A.supporters)} with {self.player_A.supporters}")
        print(f"player_B has a group of {len(self.player_B.supporters)} with {self.player_B.supporters}")
        if len(self.player_A.supporters) > len(self.player_B.supporters):
            return Winner.A
        elif len(self.player_A.supporters) < len(self.player_B.supporters):
            return Winner.B
        else:
            print("A tie.")
            return Winner.Tie

    def play(self):
        going = self.first_round(5)
        if going:
            self.second_round(2)
            self.third_round()
            win = self.winner()
            return win
        return Winner.Tie


if __name__ == "__main__":
    player_1_winning = 0
    player_2_winning = 0
    for i in range(0, 1000):
        game = Game()
        player_1 = Player(Strategy.MONK_MAX)
        player_2 = Player(Strategy.MONK_MIN)
        game.set_player(player_1, player_2)
        winner = game.play()
        if winner == Winner.A:
            player_1_winning += 1
        if winner == Winner.B:
            player_2_winning += 1
    print(f"Strategy of choosing Monk than Max winning: {player_1_winning}")
    print(f"Strategy of choosing randomly winning: {player_2_winning}")


