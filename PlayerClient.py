# %%
import socket
import os
import subprocess
import ast
import pdb
import numpy as np
import time


# %%
player_name = 'training_session'  # enter unique name for your game
s = socket.socket()
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = 'localhost'  # change ip addres to ip address of your computer or use 'localhost' to practice
port = 9999

s.connect((host, port))

while True:
    data = s.recv(1024)
    if data.decode("utf-8") == 'request_name':
        s.send(str.encode(player_name))
        client_response = str(s.recv(20480), "utf-8")
        print(client_response, end="")
        print('\n')
        break

while True:
    data = s.recv(20480)
    print(data, end=".")
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







































