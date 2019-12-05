# %% import library
import random
from collections import defaultdict
from itertools import combinations
import operator
import numpy as np


# %% single card class definition
class Card:
    """
    A single poker card in the game.
    """

    def __init__(self, rank, suit):  # initialization
        self._rank_value = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                            '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        self.rank = rank
        self.suit = suit
        self.val = self._rank_value[self.rank]

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


# %% deck class definition
class Deck:
    """
    One or more poker decks in the game, does not include jokers, a total of 52 cards.
    """

    def __init__(self, n_pack):  # initialization
        self._suit = ['C', 'D', 'H', 'S']  # Club, Diamond, Heart, Spades
        self._rank = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.packs = n_pack
        self.cards = []
        for pack in range(0, n_pack):
            for suit in self._suit:
                for rank in self._rank:
                    self.cards.append(Card(rank, suit))

    def shuffle(self):  # shuffle the deck
        random.shuffle(self.cards)

    def draw_card(self):  # returns the first card of the deck and remove it from the deck
        card = self.cards[0]
        self.cards.pop(0)
        return card


# %% single player class definition
class Player:
    """
    A single player in the game.
    """

    def __init__(self, name, hand=None, points=0):
        if hand is None:
            self.hand = []
        else:
            self.hand = hand
        self.name = name
        self.points = points
        self.self_past_rounds_commited = 0
        self.self_current_round_commited = 0
        self.in_game = True
        self.round_requirement_met = False

    def dealed_card(self, card):
        if len(self.hand) < 2:
            self.hand.append(card)
        else:
            print('***** WARNING: Cannot have more than 2 cards in hand. *****')
            return False

    def folding(self):
        self.self_past_rounds_commited += self.self_current_round_commited
        self.self_current_round_commited = 0
        print(f'You have folded.')
        self.round_requirement_met = True
        self.in_game = False
        return ['fold', self.get_info()]

    def checking(self, current_round_commited):
        if self.self_current_round_commited == current_round_commited:
            print(f'You want to check.')
            self.round_requirement_met = True
            return ['check', self.get_info()]
        else:
            print('***** WARNING: You need to match the bet. *****')
            return False

    def calling(self, current_round_commited):
        if self.points >= current_round_commited - self.self_current_round_commited:
            print(f'You called {current_round_commited - self.self_current_round_commited} points')
            self.self_current_round_commited = current_round_commited - self.self_current_round_commited
            self.points -= (current_round_commited - self.self_current_round_commited)
            self.round_requirement_met = True
            return ['call', self.get_info()]
        else:
            print('***** WARNING: You do not have enough points to call. *****')
            return False

    def raising(self, current_round_commited, raise_amount):
        if current_round_commited - self.self_current_round_commited + raise_amount <= self.points:
            self.self_current_round_commited = current_round_commited + raise_amount
            self.points -= (current_round_commited - self.self_current_round_commited) - raise_amount
            print(f'You raised {raise_amount} points in addition to the previous bet {current_round_commited} points')
            self.round_requirement_met = True
            return ['raising', raise_amount, self.get_info()]
        else:
            print(f'***** WARNING: You do not have enough to raise {raise_amount} points. *****')
            print(f'A maximum of {self.points + self.self_current_round_commited - current_round_commited} points available for raise.')
            return False

    def all_in(self):
        if self.points > 0:
            self.self_current_round_commited += self.points
            self.points = 0
            self.round_requirement_met = True
            print('You have decided to all-in.')
            return ['all-in', self.get_info()]
        else:
            print(f'***** WARNING: You already bet all your points. *****')
            return False

    def ask_for_move(self, current_round_commited):
        print(f'----- ----- ----- ----- ----- ----- Player Move ----- ----- ----- ----- ----- -----')
        print(f'You have commited {self.self_past_rounds_commited + self.self_current_round_commited} points this game.')
        if current_round_commited == self.self_current_round_commited:
            print(f'You have match the bet this round.')
        else:
            print(f'You need to commit additional {current_round_commited - self.self_current_round_commited} points.')
        exist_error = True
        while exist_error:
            move = input(f'Please select a move: (fold, check, call, raise, all-in)')
            if move == 'fold':
                outputs = self.folding()
                exist_error = False
            elif move == 'check':
                outputs = self.checking(current_round_commited)
                if isinstance(outputs, list):
                    exist_error = False
            elif move == 'call':
                outputs = self.calling(current_round_commited)
                if isinstance(outputs, list):
                    exist_error = False
            elif move == 'raise':
                amount = input(f'Please enter the amount of points to raise: ')
                try:
                    int_amount = int(amount)
                except():
                    print('***** WARNING: Entered number is invalid. *****')
                outputs = self.raising(current_round_commited, int_amount)
                if isinstance(outputs, list):
                    exist_error = False
            elif move == 'all-in':
                outputs = self.all_in()
                if isinstance(outputs, list):
                    exist_error = False

    def get_info(self):
        return [self.points, self.self_past_rounds_commited, self.self_current_round_commited,
                self.in_game, self.round_requirement_met]


# %% comparator class definition
class Comparator:
    """
    Compare a list of 7 cards group and rank based on highest hand.
    """

    def __init__(self):
        self._rank_value = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                            '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        self._hand_dict = {9: "straight flush", 8: "four of a kind", 7: "full house", 6: "flush", 5: "straight",
                           4: "three of a kind", 3: "two pairs", 2: "one pair", 1: "high card"}

    def check_one_pair(self, hand):
        values = [i[:-1] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[self._rank_value[v]] += 1
        sorted_values = sorted(value_counts.items(), key=operator.itemgetter(1), reverse=True)
        if sorted(value_counts.values()) == [1, 1, 1, 2]:
            value_counts.pop(sorted_values[0][0])
            sorted_indices = sorted(value_counts.items(), key=operator.itemgetter(0), reverse=True)
            two = sorted_values[0][0]
            one_1 = sorted_indices[0][0]
            one_2 = sorted_indices[1][0]
            one_3 = sorted_indices[2][0]
            return [2, two, one_1, one_2, one_3]
        else:
            return False

    def check_two_pairs(self, hand):
        values = [i[:-1] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[self._rank_value[v]] += 1
        sorted_values = sorted(value_counts.items(), key=operator.itemgetter(1), reverse=True)
        if sorted(value_counts.values()) == [1, 2, 2]:
            value_counts.pop(sorted_values[2][0])
            sorted_indices = sorted(value_counts.items(), key=operator.itemgetter(0), reverse=True)
            two_1 = sorted_indices[0][0]
            two_2 = sorted_indices[1][0]
            one = sorted_values[2][0]
            return [3, two_1, two_2, one]
        else:
            return False

    def check_three_of_a_kind(self, hand):
        values = [i[:-1] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[self._rank_value[v]] += 1
        sorted_values = sorted(value_counts.items(), key=operator.itemgetter(1), reverse=True)
        if set(value_counts.values()) == {3, 1}:
            value_counts.pop(sorted_values[0][0])
            sorted_indices = sorted(value_counts.items(), key=operator.itemgetter(0), reverse=True)
            three = sorted_values[0][0]
            one_1 = sorted_indices[0][0]
            one_2 = sorted_indices[1][0]
            return [4, three, one_1, one_2]
        else:
            return False

    def check_straight(self, hand):
        values = [i[:-1] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[self._rank_value[v]] += 1
        rank_values = [self._rank_value[i] for i in values]
        value_range = max(rank_values) - min(rank_values)
        if len(set(value_counts.values())) == 1 and (value_range == 4):
            return [5, int(np.mean(rank_values))]
        else:
            if set(values) == {"A", "2", "3", "4", "5"}:
                return [5, 3]
            return False

    def check_flush(self, hand):
        suits = [i[-1] for i in hand]
        if len(set(suits)) == 1:
            values = [i[:-1] for i in hand]
            value_counts = defaultdict(lambda: 0)
            for v in values:
                value_counts[self._rank_value[v]] += 1
            sorted_indices = sorted(value_counts.items(), key=operator.itemgetter(0), reverse=True)
            first = sorted_indices[0][0]
            second = sorted_indices[1][0]
            third = sorted_indices[2][0]
            fourth = sorted_indices[3][0]
            fifth = sorted_indices[4][0]
            return [6, first, second, third, fourth, fifth]
        else:
            return False

    def check_full_house(self, hand):
        values = [i[:-1] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[self._rank_value[v]] += 1
        sorted_values = sorted(value_counts.items(), key=operator.itemgetter(1), reverse=True)
        if set(value_counts.values()) == {2, 3}:
            three = sorted_values[0][0]
            two = sorted_values[1][0]
            return [7, three, two]
        return False

    def check_four_of_a_kind(self, hand):
        values = [i[:-1] for i in hand]
        value_counts = defaultdict(lambda: 0)
        for v in values:
            value_counts[self._rank_value[v]] += 1
        sorted_values = sorted(value_counts.items(), key=operator.itemgetter(1), reverse=True)
        if set(value_counts.values()) == {1, 4}:
            four = sorted_values[0][0]
            one = sorted_values[1][0]
            return [8, four, one]
        return False

    def check_straight_flush(self, hand):
        if isinstance(self.check_flush(hand), list) and isinstance(self.check_straight(hand), list):
            if self.check_straight(hand)[1] < 12:
                return [9, self.check_straight(hand)[1]]
        else:
            return False

    def check_royal_flush(self, hand):
        if isinstance(self.check_flush(hand), list) and isinstance(self.check_straight(hand), list):
            if self.check_straight(hand)[1] == 12:
                return [10]
        else:
            return False

    def check_hand(self, hand):
        if isinstance(self.check_royal_flush(hand), list):
            return self.check_royal_flush(hand)
        elif isinstance(self.check_straight_flush(hand), list):
            return self.check_straight_flush(hand)
        elif isinstance(self.check_four_of_a_kind(hand), list):
            return self.check_four_of_a_kind(hand)
        elif isinstance(self.check_full_house(hand), list):
            return self.check_full_house(hand)
        elif isinstance(self.check_flush(hand), list):
            return self.check_flush(hand)
        elif isinstance(self.check_straight(hand), list):
            return self.check_straight(hand)
        elif isinstance(self.check_three_of_a_kind(hand), list):
            return self.check_three_of_a_kind(hand)
        elif isinstance(self.check_two_pairs(hand), list):
            return self.check_two_pairs(hand)
        elif isinstance(self.check_one_pair(hand), list):
            return self.check_one_pair(hand)
        else:
            values = [i[:-1] for i in hand]
            value_counts = defaultdict(lambda: 0)
            for v in values:
                value_counts[self._rank_value[v]] += 1
            sorted_values = sorted(value_counts.items(), key=operator.itemgetter(0), reverse=True)
            first = sorted_values[0][0]
            second = sorted_values[1][0]
            third = sorted_values[2][0]
            fourth = sorted_values[3][0]
            fifth = sorted_values[4][0]
            return [1, first, second, third, fourth, fifth]

    def find_best_hand(self, cards):
        best_value = [0]
        possible_combos = combinations(cards, 5)
        for c in possible_combos:
            current_hand = list(c)
            hand_value = self.check_hand(current_hand)
            if hand_value[0] > best_value[0]:
                best_value = hand_value
            elif hand_value[0] == best_value[0]:
                for card in range(len(hand_value) - 1):
                    if hand_value[card + 1] > best_value[card + 1]:
                        best_value = hand_value
        return best_value

    def rank_cards_list(self, cards_list):
        value_counts = defaultdict(lambda: 0)
        for i in cards_list:
            value_counts[str(i)] = 0
        print(value_counts)
        possible_combos = combinations(cards_list, 2)
        for c in possible_combos:
            cards_1, cards_2 = c
            print(cards_1, cards_2)
            value_1 = self.find_best_hand(cards_1)
            value_2 = self.find_best_hand(cards_2)
            print(value_1, value_2)
            if value_1[0] > value_2[0]:
                value_counts[str(cards_1)] += 1
            elif value_1[0] < value_2[0]:
                value_counts[str(cards_2)] += 1
            else:
                for card in range(len(value_1) - 1):
                    if value_1[card + 1] > value_2[card + 1]:
                        value_counts[str(cards_1)] += 1
                        break
                    elif value_1[card + 1] < value_2[card + 1]:
                        value_counts[str(cards_2)] += 1
                        break
            print(value_counts)
        return sorted(value_counts.items(), key=operator.itemgetter(1), reverse=True)


# %% game environment class definition
class GameEnv:
    """
    Poker game environment.
    -------------------------------------------------------------------------------------------------------------------
    Input player list "players_list" is assumed to be sorted by the seat order:
        Small Blind, Big Blind, other players.


    """

    def __init__(self, players_list, small_blind_points=1, big_blind_points=2):
        self.players_list = players_list
        self.small_blind_points = small_blind_points
        self.big_blind_points = big_blind_points

        self.n_player = len(self.players_list)
        self.deck = None
        self.board = None

    def initialize_player_cards(self):
        for player in self.players_list:
            player.dealed_card(self.deck.draw_card())  # player draws 2 cards
            player.dealed_card(self.deck.draw_card())

            outputs = [player.hand]
            print(outputs)
            ##### should add output to player client "player"

    def apply_blinds(self):
        self.players_list[0].points -= self.small_blind_points  # small blind player
        self.players_list[0].self_current_round_commited = self.small_blind_points
        self.players_list[1].points -= self.big_blind_points  # big blind player
        self.players_list[1].self_current_round_commited = self.big_blind_points

    def reset(self):
        for player in self.players_list:
            player.hand = []
            player.round_requirement_met = False
            player.in_game = True
        self.deck = Deck(1)
        self.deck.shuffle()
        self.board = []

    def start_game(self):  # apply blinds and each player draws two cards
        self.reset()
        self.apply_blinds()
        self.initialize_player_cards()

    def start_round(self):  # set all players' round reqirement to not met
        for player in self.players_list:
            player.round_requirement_met = False

    def round_0_play(self):  # need to chekc number of players still in tournament
        self.start_round()
        iteration = 2  # skipping small and big blind
        round_continues = True
        current_round_commited = 2
        while round_continues:
            round_requirement = []
            player_index = self.n_player % iteration
            if player.points > 0 and player.in_game:  # check if player has all-in or folded
                outputs = [self.players_list[player_index].hand, self.board, current_round_commited]
                ##### add output to player client "self.players_list[player_index]" and ask for move
                print(outputs)

                inputs = list(['raise', 100, [1000, 150, 300, True, True]])
                ##### add input from player client "self.players_list[player_index]"
                print(inputs)

                player.points = inputs[2][0]
                player.self_past_rounds_commited = inputs[2][1]
                player.self_current_round_commited = inputs[2][2]
                player.in_game = inputs[2][3]
                player.round_requirement_met = inputs[2][4]

                if inputs[2][2] > current_round_commited:
                    current_round_commited = inputs[2][2]

                iteration += 1

                for player in self.players_list:  # append current round
                    if player.points > 0:
                        round_requirement.append(player.round_requirement_met)
                if all(item is True for item in round_requirement):  # check to end current round
                    round_continues = False

    def round_1_play(self):  # need to check for number of players still in game
        self.start_round()
        for i in range(3):  # add 3 cards to the board
            self.board.append(self.deck.draw_card())
        iteration = 0  # start at small blind
        round_continues = True
        current_round_commited = 0
        while round_continues:
            round_requirement = []
            player_index = self.n_player % iteration
            if player.points > 0 and player.in_game:  # check if player has all-in or folded
                outputs = [self.players_list[player_index].hand, self.board, current_round_commited]
                ##### add output to player client "self.players_list[player_index]" and ask for move
                print(outputs)

                inputs = list(['raise', 100, [1000, 150, 300, True, True]])
                ##### add input from player client "self.players_list[player_index]"
                print(inputs)

                player.points = inputs[2][0]
                player.self_past_rounds_commited = inputs[2][1]
                player.self_current_round_commited = inputs[2][2]
                player.in_game = inputs[2][3]
                player.round_requirement_met = inputs[2][4]

                if inputs[2][2] > current_round_commited:
                    current_round_commited = inputs[2][2]

                iteration += 1

                for player in self.players_list:  # append current round
                    if player.points > 0:
                        round_requirement.append(player.round_requirement_met)
                if all(item is True for item in round_requirement):  # check to end current round
                    round_continues = False

    def round_2_play(self):  # need to check for number of players still in game
        self.start_round()
        self.board.append(self.deck.draw_card())  # add a card to the board
        iteration = 0  # start at small blind
        round_continues = True
        current_round_commited = 0

        while round_continues:
            round_requirement = []
            player_index = self.n_player % iteration
            if player.points > 0 and player.in_game:  # check if player has all-in or folded
                outputs = [self.players_list[player_index].hand, self.board, current_round_commited]
                ##### add output to player client "self.players_list[player_index]" and ask for move
                print(outputs)

                inputs = list(['raise', 100, [1000, 150, 300, True, True]])
                ##### add input from player client "self.players_list[player_index]"
                print(inputs)

                player.points = inputs[2][0]
                player.self_past_rounds_commited = inputs[2][1]
                player.self_current_round_commited = inputs[2][2]
                player.in_game = inputs[2][3]
                player.round_requirement_met = inputs[2][4]

                if inputs[2][2] > current_round_commited:
                    current_round_commited = inputs[2][2]

                iteration += 1

                for player in self.players_list:  # append current round
                    if player.points > 0:
                        round_requirement.append(player.round_requirement_met)
                if all(item is True for item in round_requirement):  # check to end current round
                    round_continues = False

    def round_3_play(self):  # need to check for number of players still in game
        self.start_round()
        self.board.append(self.deck.draw_card())  # add a card to the board
        iteration = 0  # start at small blind
        round_continues = True
        current_round_commited = 0

        while round_continues:
            round_requirement = []
            player_index = self.n_player % iteration
            if player.points > 0 and player.in_game:  # check if player has all-in or folded
                outputs = [self.players_list[player_index].hand, self.board, current_round_commited]
                ##### add output to player client "self.players_list[player_index]" and ask for move
                print(outputs)

                inputs = list(['raise', 100, [1000, 150, 300, True, True]])
                ##### add input from player client "self.players_list[player_index]"
                print(inputs)

                player.points = inputs[2][0]
                player.self_past_rounds_commited = inputs[2][1]
                player.self_current_round_commited = inputs[2][2]
                player.in_game = inputs[2][3]
                player.round_requirement_met = inputs[2][4]

                if inputs[0] == 'raise':
                    current_round_commited += inputs[1]

                iteration += 1

                for player in self.players_list:  # append current round
                    if player.points > 0:
                        round_requirement.append(player.round_requirement_met)
                if all(item is True for item in round_requirement):  # check to end current round
                    round_continues = False


# %%
cards = [["AH", "JH", "7D", "QC", "QH", "2H", "10H"],
         ["9H", "JH", "7D", "3C", "QH", "10H", "KH"],
         ["QH", "4H", "7D", "QC", "QS", "2H", "10H"],
         ["AH", "6H", "7D", "QC", "5H", "2H", "10H"],
         ["3H", "JH", "7D", "QC", "QH", "2H", "4H"]]
a = Comparator()
a.rank_cards_list(cards)

























