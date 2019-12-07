# %% import library
import ast
import random
from collections import defaultdict
from itertools import combinations
import operator
import numpy as np
import pandas as pd
from math import floor


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

    def __init__(self, name, conn, hand=None, points=0):
        if hand is None:
            self.hand = []
        else:
            self.hand = hand
        self.name = name
        self.conn = conn
        self.points = points
        self.self_past_rounds_commited = 0
        self.self_current_round_commited = 0
        self.in_game = True
        self.round_requirement_met = False
        self.exist_error = True

        self.all_available_cards = None
        self.best_hand_rating = None
        self.game_end_return = 0

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
        return {'MOVE': 'fold',
                'POINTS': self.points,
                'PAST_COMMITED': self.self_past_rounds_commited,
                'CURRENT_COMMITED': self.self_current_round_commited,
                'IN_GAME': self.in_game,
                'BET_MATCH': self.round_requirement_met}

    def checking(self, current_round_commited):
        if self.self_current_round_commited == current_round_commited:
            print(f'You want to check.')
            self.round_requirement_met = True
            return {'MOVE': 'check',
                    'POINTS': self.points,
                    'PAST_COMMITED': self.self_past_rounds_commited,
                    'CURRENT_COMMITED': self.self_current_round_commited,
                    'IN_GAME': self.in_game,
                    'BET_MATCH': self.round_requirement_met}
        else:
            print('***** WARNING: You need to match the bet. *****')
            return False

    def calling(self, current_round_commited):
        if self.points >= current_round_commited - self.self_current_round_commited:
            print(f'You called {current_round_commited - self.self_current_round_commited} points.')
            self.points -= (current_round_commited - self.self_current_round_commited)
            self.self_current_round_commited = current_round_commited
            self.round_requirement_met = True
            return {'MOVE': 'call',
                    'POINTS': self.points,
                    'PAST_COMMITED': self.self_past_rounds_commited,
                    'CURRENT_COMMITED': self.self_current_round_commited,
                    'IN_GAME': self.in_game,
                    'BET_MATCH': self.round_requirement_met}
        else:
            print('***** WARNING: You do not have enough points to call. *****')
            return False

    def raising(self, current_round_commited, raise_amount):
        if current_round_commited - self.self_current_round_commited + raise_amount <= self.points:
            self.points -= current_round_commited - self.self_current_round_commited + raise_amount
            self.self_current_round_commited = current_round_commited + raise_amount
            print(f'You raised {raise_amount} points in addition to the previous bet of {current_round_commited} points.')
            self.round_requirement_met = True
            return {'MOVE': 'raising',
                    'RAISE_AMOUNT': raise_amount,
                    'POINTS': self.points,
                    'PAST_COMMITED': self.self_past_rounds_commited,
                    'CURRENT_COMMITED': self.self_current_round_commited,
                    'IN_GAME': self.in_game,
                    'BET_MATCH': self.round_requirement_met}
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
            return {'MOVE': 'all_in',
                    'POINTS': self.points,
                    'PAST_COMMITED': self.self_past_rounds_commited,
                    'CURRENT_COMMITED': self.self_current_round_commited,
                    'IN_GAME': self.in_game,
                    'BET_MATCH': self.round_requirement_met}
        else:
            print(f'***** WARNING: You already bet all your points. *****')
            return False

    def ask_for_move(self, current_round_commited):
        print(f'You have commited {self.self_past_rounds_commited + self.self_current_round_commited} points this game.')
        if current_round_commited == self.self_current_round_commited:
            print(f'You have matched the bet this round.')
        else:
            print(f'You need to commit additional {current_round_commited - self.self_current_round_commited} points.')
        self.exist_error = True
        while self.exist_error:
            move = input(f'Please select a move: (fold, check, call, raising, all_in)')
            if move == 'fold':
                outputs = self.folding()
                self.exist_error = False
            elif move == 'check':
                outputs = self.checking(current_round_commited)
                if isinstance(outputs, dict):
                    self.exist_error = False
            elif move == 'call':
                outputs = self.calling(current_round_commited)
                if isinstance(outputs, dict):
                    self.exist_error = False
            elif move == 'raising':
                amount = input(f'Please enter the amount of points to raise: ')
                try:
                    int_amount = int(amount)
                    outputs = self.raising(current_round_commited, int_amount)
                    if isinstance(outputs, dict):
                        self.exist_error = False
                except():
                    print('***** WARNING: Entered points to raise is invalid. *****')
                    print('\n')
            elif move == 'all_in':
                outputs = self.all_in()
                if isinstance(outputs, dict):
                    self.exist_error = False
            if not self.exist_error:
                return outputs

    def get_info(self):
        return {'POINTS': self.points,
                'PAST_COMMITED': self.self_past_rounds_commited,
                'CURRENT_COMMITED': self.self_current_round_commited,
                'IN_GAME': self.in_game,
                'BET_MATCH': self.round_requirement_met}


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
    def num2hand(self, rating):
        return self._hand_dict[rating]

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

    def __init__(self, players_list, small_blind_points=1, big_blind_points=2, recording=True):
        self.players_list = players_list
        self.small_blind_points = small_blind_points
        self.big_blind_points = big_blind_points

        self.n_player = len(self.players_list)
        self.deck = None
        self.board = None

        self.record_out = pd.DataFrame()

    @staticmethod
    def communication(conn, cmd):
        conn.send(str.encode(cmd))  # sending command to player client
        print(f'Sent command: {cmd}')
        player_response = str(conn.recv(20480), "utf-8")  # receiving message from player client
        print(f'Received message: {player_response}')
        return player_response

    def initialize_player_cards(self):
        outputs = {}
        for player in self.players_list:
            print(f'----- Initialize hands for player {player.name} -----')
            player.dealed_card(self.deck.draw_card())  # player draws a card
            outputs['first_card'] = str(player.hand[0])
            player.dealed_card(self.deck.draw_card())  # player draws another card
            outputs['second_card'] = str(player.hand[1])

            if self.communication(player.conn, 'sending_initial_hand') == 'acknowledged_initial_hand':
                player.conn.send(str.encode(str(outputs)))

    def apply_blinds(self):
        print(f'----- apply blinds for players -----')
        self.players_list[0].points -= self.small_blind_points  # small blind player
        self.players_list[0].self_current_round_commited = self.small_blind_points
        if self.communication(self.players_list[0].conn, 'sending_small_blind') == 'acknowledged_small_blind':
            self.players_list[0].conn.send(str.encode(str(self.small_blind_points)))

        self.players_list[1].points -= self.big_blind_points  # big blind player
        self.players_list[1].self_current_round_commited = self.big_blind_points
        if self.communication(self.players_list[1].conn, 'sending_big_blind') == 'acknowledged_big_blind':
            self.players_list[1].conn.send(str.encode(str(self.big_blind_points)))

    def initial_points(self, initial_points=1000):
        for player in self.players_list:
            print(f'----- ----- Initialize points for player {player.name} ----- -----')
            if self.communication(player.conn, 'sending_initial_points') == 'acknowledged_initial_points':
                player.conn.send(str.encode(str(initial_points)))
                player.points = initial_points

    def reset(self):
        print(self.players_list)
        for player in self.players_list:
            player.hand = []
            player.round_requirement_met = False
            player.in_game = True
            player.all_available_cards = None
            player.best_hand_rating = None
            player.game_end_return = 0
            self.communication(player.conn, 'game_start_reset')
        self.deck = Deck(1)
        self.deck.shuffle()
        self.board = []

    def game_start_setup(self):  # distribute initial points apply blinds and each player draws two cards
        print(f'----- ----- ----- ----- ----- ----- ----- ---- ----- ----- ----- ----- ----- -----')
        print(f'----- ----- ----- ----- ----- ----- Game Start ----- ----- ----- ----- ----- -----')
        print(f'----- ----- ----- ----- ----- ----- ----- ---- ----- ----- ----- ----- ----- -----')
        self.reset()
        self.apply_blinds()
        self.initialize_player_cards()

    def round_start_setup(self, round_0=False):  # set all players' round reqirement to not met
        for player in self.players_list:
            player.round_requirement_met = False
            if player.name == self.players_list[1].name and round_0:
                player.round_requirement_met = True

    def round_0_play(self):  # need to check number of players still in tournament
        print(f'----- ----- ----- ----- Round 0 Starts ----- ----- ----- -----')
        self.round_start_setup(round_0=True)
        iteration = 2  # skipping small and big blind
        round_continues = True
        current_round_commited = 2
        while round_continues:
            round_requirement = [True]
            player_index = iteration % self.n_player
            if self.players_list[player_index].points > 0 and self.players_list[player_index].in_game:  # check if player has all-in or folded
                print(f'----- Player {self.players_list[player_index].name} move -----')

                outputs = {'HAND': str(self.players_list[player_index].hand),
                           'BOARD': str(self.board),
                           'CURRENT_BET': str(current_round_commited)}
                if self.communication(self.players_list[player_index].conn, 'request_round_0_move') == 'acknowledged_request':
                    self.players_list[player_index].conn.send(str.encode(str(outputs)))

                player_info = str(self.players_list[player_index].conn.recv(20480), "utf-8")
                player_info = ast.literal_eval(player_info)
                print(f'Received player info: {player_info}')

                self.players_list[player_index].points = player_info['POINTS']
                self.players_list[player_index].self_past_rounds_commited = player_info['PAST_COMMITED']
                self.players_list[player_index].self_current_round_commited = player_info['CURRENT_COMMITED']
                self.players_list[player_index].in_game = player_info['IN_GAME']
                self.players_list[player_index].round_requirement_met = player_info['BET_MATCH']
                if player_info['CURRENT_COMMITED'] > current_round_commited:
                    current_round_commited = player_info['CURRENT_COMMITED']
                iteration += 1
                if player_info['MOVE'] != 'raising':
                    for player in self.players_list:  # append current round
                        if player.points >= 0 and player.in_game:
                            round_requirement.append(player.round_requirement_met)
                    if all(item is True for item in round_requirement):  # check to end current round
                        if current_round_commited == 2:
                            round_continues = False
            if round_continues is False:
                for player in self.players_list:
                    print(f'----- ----- ----- Player {self.players_list[player_index].name} Round End Update ----- ----- -----')
                    player.self_past_rounds_commited += player.self_current_round_commited
                    player.self_current_round_commited = 0
                    self.communication(player.conn, 'round_end_update')
        print(f'----- ----- ----- ----- Round 0 Ends ----- ----- ----- -----')

    def round_1_play(self):
        print(f'----- ----- ----- ----- Round 1 Starts ----- ----- ----- -----')
        self.round_start_setup()
        for i in range(3):  # add 3 cards to the board
            self.board.append(self.deck.draw_card())
        iteration = 0  # start at small blind
        round_continues = True
        current_round_commited = 0
        while round_continues:
            round_requirement = [True]
            player_index = iteration % self.n_player
            if self.players_list[player_index].points > 0 and self.players_list[player_index].in_game:  # check if player has all-in or folded
                print(f'----- Player {self.players_list[player_index].name} move -----')

                outputs = {'HAND': str(self.players_list[player_index].hand),
                           'BOARD': str(self.board),
                           'CURRENT_BET': str(current_round_commited)}
                if self.communication(self.players_list[player_index].conn,
                                      'request_round_1_move') == 'acknowledged_request':
                    self.players_list[player_index].conn.send(str.encode(str(outputs)))

                player_info = str(self.players_list[player_index].conn.recv(20480), "utf-8")
                player_info = ast.literal_eval(player_info)
                print(f'Received player info: {player_info}')

                self.players_list[player_index].points = player_info['POINTS']
                self.players_list[player_index].self_past_rounds_commited = player_info['PAST_COMMITED']
                self.players_list[player_index].self_current_round_commited = player_info['CURRENT_COMMITED']
                self.players_list[player_index].in_game = player_info['IN_GAME']
                self.players_list[player_index].round_requirement_met = player_info['BET_MATCH']
                if player_info['CURRENT_COMMITED'] > current_round_commited:
                    current_round_commited = player_info['CURRENT_COMMITED']
                iteration += 1
                if player_info['MOVE'] != 'raising':
                    for player in self.players_list:  # append current round
                        if player.points >= 0 and player.in_game:
                            round_requirement.append(player.round_requirement_met)
                    if all(item is True for item in round_requirement):  # check to end current round
                        round_continues = False
                if round_continues is False:
                    print(f'----- ----- ----- Round End Update ----- ----- -----')
                    for player in self.players_list:
                        player.self_past_rounds_commited += player.self_current_round_commited
                        player.self_current_round_commited = 0
                        self.communication(self.players_list[player_index].conn, 'round_end_update')
        print(f'----- ----- ----- ----- Round 1 Ends ----- ----- ----- -----')

    def round_2_play(self):
        print(f'----- ----- ----- ----- Round 2 Starts ----- ----- ----- -----')
        self.round_start_setup()
        self.board.append(self.deck.draw_card())  # add a card to the board
        iteration = 0  # start at small blind
        round_continues = True
        current_round_commited = 0
        while round_continues:
            round_requirement = [True]
            player_index = iteration % self.n_player
            if self.players_list[player_index].points > 0 and self.players_list[player_index].in_game:  # check if player has all-in or folded
                print(f'----- Player {self.players_list[player_index].name} move -----')

                outputs = {'HAND': str(self.players_list[player_index].hand),
                           'BOARD': str(self.board),
                           'CURRENT_BET': str(current_round_commited)}
                if self.communication(self.players_list[player_index].conn,
                                      'request_round_2_move') == 'acknowledged_request':
                    self.players_list[player_index].conn.send(str.encode(str(outputs)))

                player_info = str(self.players_list[player_index].conn.recv(20480), "utf-8")
                player_info = ast.literal_eval(player_info)
                print(f'Received player info: {player_info}')

                self.players_list[player_index].points = player_info['POINTS']
                self.players_list[player_index].self_past_rounds_commited = player_info['PAST_COMMITED']
                self.players_list[player_index].self_current_round_commited = player_info['CURRENT_COMMITED']
                self.players_list[player_index].in_game = player_info['IN_GAME']
                self.players_list[player_index].round_requirement_met = player_info['BET_MATCH']
                if player_info['CURRENT_COMMITED'] > current_round_commited:
                    current_round_commited = player_info['CURRENT_COMMITED']
                iteration += 1
                if player_info['MOVE'] != 'raising':
                    for player in self.players_list:  # append current round
                        if player.points >= 0 and player.in_game:
                            round_requirement.append(player.round_requirement_met)
                    if all(item is True for item in round_requirement):  # check to end current round
                        round_continues = False
                if round_continues is False:
                    print(f'----- ----- ----- Round End Update ----- ----- -----')
                    for player in self.players_list:
                        player.self_past_rounds_commited += player.self_current_round_commited
                        player.self_current_round_commited = 0
                        self.communication(self.players_list[player_index].conn, 'round_end_update')
        print(f'----- ----- ----- ----- Round 2 Ends ----- ----- ----- -----')

    def round_3_play(self):
        print(f'----- ----- ----- ----- Round 3 Starts ----- ----- ----- -----')
        self.round_start_setup()
        self.board.append(self.deck.draw_card())  # add a card to the board
        iteration = 0  # start at small blind
        round_continues = True
        current_round_commited = 0
        while round_continues:
            round_requirement = [True]
            player_index = iteration % self.n_player
            if self.players_list[player_index].points > 0 and self.players_list[player_index].in_game:  # check if player has all-in or folded
                print(f'----- Player {self.players_list[player_index].name} move -----')

                outputs = {'HAND': str(self.players_list[player_index].hand),
                           'BOARD': str(self.board),
                           'CURRENT_BET': str(current_round_commited)}
                if self.communication(self.players_list[player_index].conn,
                                      'request_round_3_move') == 'acknowledged_request':
                    self.players_list[player_index].conn.send(str.encode(str(outputs)))

                player_info = str(self.players_list[player_index].conn.recv(20480), "utf-8")
                player_info = ast.literal_eval(player_info)
                print(f'Received player info: {player_info}')

                self.players_list[player_index].points = player_info['POINTS']
                self.players_list[player_index].self_past_rounds_commited = player_info['PAST_COMMITED']
                self.players_list[player_index].self_current_round_commited = player_info['CURRENT_COMMITED']
                self.players_list[player_index].in_game = player_info['IN_GAME']
                self.players_list[player_index].round_requirement_met = player_info['BET_MATCH']
                if player_info['CURRENT_COMMITED'] > current_round_commited:
                    current_round_commited = player_info['CURRENT_COMMITED']
                iteration += 1
                if player_info['MOVE'] != 'raising':
                    for player in self.players_list:
                        if player.points >= 0 and player.in_game:
                            round_requirement.append(player.round_requirement_met)
                    if all(item is True for item in round_requirement):  # check to end current round
                        round_continues = False
                if round_continues is False:
                    print(f'----- ----- ----- Round End Update ----- ----- -----')
                    for player in self.players_list:
                        player.self_past_rounds_commited += player.self_current_round_commited
                        player.self_current_round_commited = 0
                        self.communication(self.players_list[player_index].conn, 'round_end_update')
        print(f'----- ----- ----- ----- Round 3 Ends ----- ----- ----- -----')

    def game_end_update(self):
        print(f'----- ----- ----- ----- ----- Game End Update ----- ----- ----- ----- -----')
        comparator = Comparator()
        hand_dict = {}
        commited_dict = {}
        return_dict = {}
        points_list = []
        index_list = []
        cards_list = []
        for index in range(len(self.players_list)):
            if self.players_list[index].in_game:
                hand_dict.update({self.players_list[index].name: self.players_list[index].hand})

                self.players_list[index].self_past_rounds_commited += self.players_list[index].self_current_rounds_commited
                self.players_list[index].self_current_rounds_commited = 0
                commited_dict.update({self.players_list[index].name: self.players_list[index].self_past_rounds_commited})

                points_list.append(self.players_list[index].self_past_rounds_commited)

                all_available_cards = self.board
                for card in self.players_list[index].hand:
                    all_available_cards.append(card)
                self.players_list[index].all_available_cards = all_available_cards
                index_list.append(index)
                cards_list.append(all_available_cards)

        rank_list = comparator.rank_cards_list(cards_list)
        ranks = [i[1] for i in rank_list]
        ranks_set = set(ranks)
        for rank in np.arange(-1, -len(ranks_set), -1):
            if sum(points_list) > 0:
                winner_bet_total = 0
                rank_list_temp = list(filter(None, [i[0] if i[1] == ranks[rank] else None for i in rank_list]))
                for player in self.players_list:
                    if str(player.all_available_cards) in rank_list_temp:
                        winner_bet_total += player.self_past_rounds_commited
                winner_points_list = [min(winner_bet_total, i) for i in points_list]
                points_list = list(np.array(points_list) - np.array(winner_points_list))
                for player in self.players_list:
                    if str(player.all_available_cards) in rank_list_temp:
                        player.game_end_return = floor(sum(winner_points_list) *
                                                       player.self_past_rounds_commited/winner_bet_total)
                    return_dict.update({self.players_list[index].name: self.players_list[index].game_end_return})

        # print(f'Remaining player hands: {hand_dict}')
        # print(f'Player bets: {commited_dict}')
        # print(f'Player returns: {return_dict}')

        for player in self.players_list:
            print(f'----- ----- ----- ----- Game End Player {player.name} Update ----- ----- ----- -----')
            if self.communication(player.conn, 'game_end_hand_update') == 'acknowledged_game_end_hand_update':
                player.conn.send(str.encode(str(hand_dict)))

            if self.communication(player.conn, 'game_end_bet_update') == 'acknowledged_game_end_bet_update':
                player.conn.send(str.encode(str(commited_dict)))

            if self.communication(player.conn, 'game_end_return_update') == 'acknowledged_game_end_return_update':
                player.conn.send(str.encode(str(return_dict)))

            outputs = {'TOTAL_COMMITED': player.self_past_rounds_commited,
                       'END_RETURN': player.game_end_return,
                       'BOARD': self.board,
                       'YOUR_HAND': player.hand,
                       'YOUR_BEST_HAND': comparator.num2hand(comparator.find_best_hand(player.all_available_cards)[0])}
            if self.communication(player.conn, 'game_end_points_update') == 'acknowledged_game_end_points_update':
                player.conn.send(str.encode(str(outputs)))

            player.points += player.game_end_return
            self.players_list.append(self.players_list[0])
            self.players_list.pop(0)


# %%
# cards = [["AH", "JH", "7D", "QC", "QH", "2H", "10H"],
#          ["9H", "JH", "7D", "3C", "QH", "10H", "KH"],
#          ["QH", "4H", "7D", "QC", "QS", "2H", "10H"],
#          ["AH", "6H", "7D", "QC", "5H", "2H", "10H"],
#          ["3H", "JH", "7D", "QC", "QH", "2H", "4H"]]
# a = Comparator()
# b = a.rank_cards_list(cards)
#
#
#
# x = np.array([2, 4, 5, 4])
# len(np.where(x == 4)[0])
#
# x[[1, 2]]
# set([i[1] for i in b])
#
# list(filter(None, [i[0] if i[1] == 4 else None for i in b]))
#
#
#
# sum([2, 4, 5, 4])
#
#
# list(np.array([2, 4, 5, 4]) - np.array([2, 4, 5, 4]))
#
# import socket
# hostname = socket.gethostname()
# IPAddr = socket.gethostbyname(hostname)
# print("Your Computer Name is:" + hostname)
# print("Your Computer IP Address is:" + IPAddr)







