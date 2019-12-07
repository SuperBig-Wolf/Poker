# %%
import socket
# import json
# import os
# import subprocess
# import ast
# import pdb
# import numpy as np
# import time
from texas_holdem import *


# %% player client parameters
PLAYER_NAME = 'Zehan'
HOST = 'localhost'
PORT = 12345


# %%
player_agent = Player(PLAYER_NAME, None)
s = socket.socket()
s.connect((HOST, PORT))

while True:
    data = s.recv(1024)
    if data.decode("utf-8") == 'request_name':
        print(f'----- ----- ----- ----- ----- ----- Set Player Name ----- ----- ----- ----- ----- -----')
        print(f'Received command: request_name')
        s.send(str.encode(PLAYER_NAME))
        print(f'Sent message: {PLAYER_NAME}')
        client_response = str(s.recv(20480), "utf-8")
        # print(client_response, end="")
        # print('\n')
        break

while True:
    data = s.recv(20480)
    # print(data, end=".")

    if data.decode("utf-8") == f'sending_initial_points':
        print(f'----- ----- ----- ----- ----- ----- Receive Initial Points ----- ----- ----- ----- ----- -----')
        print(f'Received command: sending_initial_points')

        my_response = 'acknowledged_initial_points'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        initial_points = str(s.recv(20480), "utf-8")
        print(f'Received initial points: {int(initial_points)}')
        player_agent.points = int(initial_points)

    if data.decode("utf-8") == f'game_start_reset':
        print(f'----- ----- ----- ----- ----- ----- ----- ---- ----- ----- ----- ----- ----- -----')
        print(f'----- ----- ----- ----- ----- ----- Game Start ----- ----- ----- ----- ----- -----')
        print(f'----- ----- ----- ----- ----- ----- ----- ---- ----- ----- ----- ----- ----- -----')
        print(f'Received command: game_start_reset')

        player_agent.hand = []
        player_agent.round_requirement_met = False
        player_agent.in_game = True

        my_response = 'acknowledged_game_start_reset'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

    if data.decode("utf-8") == f'sending_small_blind':
        print(f'----- ----- ----- ----- ----- ----- Set Small Blind ----- ----- ----- ----- ----- -----')
        print(f'Received command: sending_small_blind')

        my_response = 'acknowledged_small_blind'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        small_blind = str(s.recv(20480), "utf-8")
        print(f'Received small blind: {small_blind}')
        player_agent.points -= int(small_blind)
        player_agent.self_current_round_commited = int(small_blind)

    if data.decode("utf-8") == f'sending_big_blind':
        print(f'----- ----- ----- ----- ----- ----- Set Big Blind ----- ----- ----- ----- ----- -----')
        print(f'Received command: sending_big_blind')

        my_response = 'acknowledged_big_blind'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        big_blind = str(s.recv(20480), "utf-8")
        print(f'Received big blind: {big_blind}')
        player_agent.points -= int(big_blind)
        player_agent.self_current_round_commited = int(big_blind)

    if data.decode("utf-8") == f'sending_initial_hand':
        print(f'----- ----- ----- ----- ----- ----- Receive Initial Hand ----- ----- ----- ----- ----- -----')
        print(f'Received command: sending_initial_hand')

        my_response = 'acknowledged_initial_hand'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        initial_hands = str(s.recv(20480), "utf-8")
        initial_hands = ast.literal_eval(initial_hands)
        print(f'Received initial hands: {initial_hands}')
        player_agent.dealed_card(initial_hands['first_card'])
        player_agent.dealed_card(initial_hands['second_card'])

    if data.decode("utf-8") == f'request_round_0_move':
        print(f'----- ----- ----- ----- ----- ----- Player Round 0 Move ----- ----- ----- ----- ----- -----')
        print(f'Received command: request_round_0_move')

        my_response = 'acknowledged_request'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        player_agent.round_requirement_met = False

        game_info = str(s.recv(20480), "utf-8")
        game_info = ast.literal_eval(game_info)
        print(f'Received game info: {game_info}')

        my_response = player_agent.ask_for_move(int(game_info['CURRENT_BET']))
        print(f'Sent player info: {my_response}')
        s.send(str.encode(str(my_response)))

    if data.decode("utf-8") == f'round_end_update':
        print(f'----- ----- ----- ----- ----- ----- Round End Update ----- ----- ----- ----- ----- -----')
        print(f'Received command: round_end_update')

        player_agent.self_past_rounds_commited += player_agent.self_current_round_commited
        player_agent.self_current_round_commited = 0

        my_response = 'acknowledged_round_end_update'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

    if data.decode("utf-8") == f'request_round_1_move':
        print(f'----- ----- ----- ----- ----- ----- Player Round 1 Move ----- ----- ----- ----- ----- -----')
        print(f'Received command: request_round_1_move')

        my_response = 'acknowledged_request'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        player_agent.round_requirement_met = False

        game_info = str(s.recv(20480), "utf-8")
        game_info = ast.literal_eval(game_info)
        print(f'Received game info: {game_info}')

        my_response = player_agent.ask_for_move(int(game_info['CURRENT_BET']))
        print(f'Sent player info: {my_response}')
        s.send(str.encode(str(my_response)))

    if data.decode("utf-8") == f'request_round_2_move':
        print(f'----- ----- ----- ----- ----- ----- Player Round 2 Move ----- ----- ----- ----- ----- -----')
        print(f'Received command: request_round_2_move')

        my_response = 'acknowledged_request'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        player_agent.round_requirement_met = False

        game_info = str(s.recv(20480), "utf-8")
        game_info = ast.literal_eval(game_info)
        print(f'Received game info: {game_info}')

        my_response = player_agent.ask_for_move(int(game_info['CURRENT_BET']))
        print(f'Sent player info: {my_response}')
        s.send(str.encode(str(my_response)))

    if data.decode("utf-8") == f'request_round_3_move':
        print(f'----- ----- ----- ----- ----- ----- Player Round 3 Move ----- ----- ----- ----- ----- -----')
        print(f'Received command: request_round_3_move')

        my_response = 'acknowledged_request'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        player_agent.round_requirement_met = False

        game_info = str(s.recv(20480), "utf-8")
        game_info = ast.literal_eval(game_info)
        print(f'Received game info: {game_info}')

        my_response = player_agent.ask_for_move(int(game_info['CURRENT_BET']))
        print(f'Sent player info: {my_response}')
        s.send(str.encode(str(my_response)))

    if data.decode("utf-8") == f'game_end_hand_update':
        print(f'----- ----- ----- ----- ----- ----- Game End Hand Update ----- ----- ----- ----- ----- -----')
        print(f'Received command: game_end_hand_update')

        my_response = 'acknowledged_game_end_hand_update'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        hand_info = str(s.recv(20480), "utf-8")
        hand_info = ast.literal_eval(hand_info)
        print(f'Received hand info: {hand_info}')

    if data.decode("utf-8") == f'game_end_bet_update':
        print(f'----- ----- ----- ----- ----- ----- Game End Bet Update ----- ----- ----- ----- ----- -----')
        print(f'Received command: game_end_bet_update')

        my_response = 'acknowledged_game_end_bet_update'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        bet_info = str(s.recv(20480), "utf-8")
        bet_info = ast.literal_eval(bet_info)
        print(f'Received bet info: {bet_info}')

    if data.decode("utf-8") == f'game_end_return_update':
        print(f'----- ----- ----- ----- ----- ----- Game End Return Update ----- ----- ----- ----- ----- -----')
        print(f'Received command: game_end_return_update')

        my_response = 'acknowledged_game_end_return_update'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        return_info = str(s.recv(20480), "utf-8")
        return_info = ast.literal_eval(return_info)
        print(f'Received return info: {bet_info}')

    if data.decode("utf-8") == f'game_end_points_update':
        print(f'----- ----- ----- ----- ----- ----- Game End Points Update ----- ----- ----- ----- ----- -----')
        print(f'Received command: game_end_points_update')

        my_response = 'acknowledged_game_end_points_update'
        print(f'Sent message: {my_response}')
        s.send(str.encode(my_response))

        points_info = str(s.recv(20480), "utf-8")
        points_info = ast.literal_eval(points_info)
        print(f'Received return info: {points_info}')

        player_agent.points += int(points_info['RETURN'])

































    if data.decode("utf-8") == f'sendinfo':
        s.send(str.encode("acknowledged_pick"))

        # Here you will recieve information about the player such as card rank, card suit, stash score.
        client_response = str(s.recv(20480), "utf-8")
        print(client_response)

        action = np.random.randint(0, 2)

        print("action pick ", action)
        s.send(str.encode(str(action)))
    if data.decode("utf-8") == f'sendaction_for_card_drop':
        s.send(str.encode("acknowledged_drop"))
        ro = str(s.recv(20480), "utf-8")
        ro = ast.literal_eval(ro)
        print("action send for drop")
        print(ro)

        # Follow the same procedure as above to send observations to your agent
        # Look at the above observations and action in variable action

        action = np.random.randint(0, 3)

        s.send(str.encode(str(action)))
        print("action drop", action)
    if data.decode("utf-8") == 'gameover':
        print("Game over wait for others to play and wait for results")
        break
    if data.decode("utf-8") == 'round_over':
        s.send(str.encode("acknowledged_round_over"))
        print('Round over')
        client_response = str(s.recv(20480), "utf-8")
        print(client_response, end="")







































