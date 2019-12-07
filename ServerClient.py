# %% import libraries
import json
import socket
import threading
from queue import Queue
from texas_holdem import *


# %% server parameters
N_THREADS = 2
JOB_NUMBER = [1, 2]
QUEUE = Queue()
ALL_CONNECTIONS = []
ALL_ADDRESSES = []
COUNT = [0]
NAMES = []
STORAGE = {}
ENV = None

host = ''
port = 12345
s = None

# scores = []
# median = 0


# %% create worker threads
def create_workers():
    for _ in range(N_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# %% create jobs
def create_jobs():
    for x in JOB_NUMBER:
        QUEUE.put(x)
    QUEUE.join()


# %% do next job that is in the queue (handle connections, send commands)
def work():
    while True:
        x = QUEUE.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_command()
        QUEUE.task_done()


# %% create a socket that connects two computers
def create_socket():
    try:
        global host
        global port
        global s

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(True)
    except socket.error as msg:
        print(f'***** WARNING: Socket creation error: {str(msg)} *****')


# %% binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        s.bind((host, port))
        s.listen(5)
        print(f'Binded the Port: {str(port)}')
    except socket.error as msg:
        print(f'***** WARNING: Socket binding error {str(msg)} ***** \nRetrying...')
        bind_socket()


# %% handling connection from multiple clients and saving to a list, closing previous connections when script is restarted
# count = [0]
def accepting_connections():
    global COUNT

    for c in ALL_CONNECTIONS:
        c.close()

    del ALL_CONNECTIONS[:]
    del ALL_ADDRESSES[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout

            ALL_CONNECTIONS.append(conn)
            ALL_ADDRESSES.append(address)

            c = COUNT[0]
            c = c + 1
            print(f'A connection has been established | IP: {address[0]} | PORT: {address[1]} | Total players: {c}')
            COUNT[:] = []
            COUNT.append(c)
        except():
            print("***** WARNING: Error accepting connections. *****")


# %% start command prompt
def start_command():
    while True:
        cmd = input('Enter command >>> ')
        if cmd == 'list':
            test_connections()
        elif 'all' in cmd:
            start_collect()
        elif 'game' in cmd:
            start_game()
        # elif 'win' in cmd:
        #     start_win()
        # elif 'select' in cmd:
        #     conn = get_target(cmd)
        #     if conn is not None:
        #         get_player_name(conn)
        else:
            print("***** WARNING: Command not recognized. *****")


# %% test all connections
def test_connections():
    results = ''
    for i, conn in enumerate(ALL_CONNECTIONS):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except():
            del ALL_CONNECTIONS[i]
            del ALL_ADDRESSES[i]
            continue
        results = str(i) + "   " + str(ALL_ADDRESSES[i][0]) + "   " + str(ALL_ADDRESSES[i][1]) + "\n"
    print("---- Clients ----" + "\n" + results)


# %% collect each player's name
def start_collect():
    global NAMES
    global STORAGE
    f = len(ALL_CONNECTIONS)
    for i in range(f):
        cmd = i
        conn, ip, pt = get_target(cmd)
        if conn is not None:
            setup_player(conn, ip, pt)
    print(f'Collected all names. | Player list: {NAMES}')


# %% selecting the target
def get_target(cmd):
    try:
        target = cmd
        conn = ALL_CONNECTIONS[target]
        ip = ALL_ADDRESSES[target][0]
        pt = ALL_ADDRESSES[target][1]
        print(f'Connection to {str(ALL_ADDRESSES[target][0])} established.')
        return conn, ip, pt
    except():
        print("***** WARNING: Selection not valid. *****")
        return None


# %% request player name
def setup_player(conn, ip, pt):
    while True:
        try:
            cmd = 'request_name'
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))  # sending command to player client
                print(f'Sent command: {cmd}')

                player_response = str(conn.recv(20480), "utf-8")  # receiving message from player client
                print(f'Received message: {player_response}')

                NAMES.append(player_response)
                print(f'Player names: {NAMES}')

                STORAGE[player_response] = {'CONN': conn, 'IP': ip, 'PORT': pt,
                                            'PLAYER': Player(player_response, conn)}
                print(f'{player_response}: {STORAGE[player_response]}')

                conn.send(str.encode("Connection established, names collected."))
                break
        except():
            print("***** WARNING: Error requesting player name. *****")
            break


# %% start a single game
def start_game():
    global ENV
    global STORAGE
    global NAMES

    ENV = GameEnv([STORAGE[player]['PLAYER'] for player in NAMES], small_blind_points=1, big_blind_points=2)

    ENV.initial_points(initial_points=1000)

    ENV.game_start_setup()
    ENV.round_0_play()
    ENV.round_1_play()
    ENV.round_2_play()
    ENV.round_3_play()


# %%
# display all current active connections with client
# def start_win():
#     NAMES[1], NAMES[0] = zip(*sorted(zip(NAMES[1], NAMES[0])))
#     k = len(NAMES[0])
#     for i in range(k):
#         print(f'Player : {NAMES[0][i]} , Score: {NAMES[1][i]}')
#
#
#
#
#
# def start_result():
#     f = len(ALL_CONNECTIONS)
#     # To be changed to select number of players
#     step_size = 4
#     for i in range(0, f, step_size):
#         cmd = i
#         conns = []
#         grp_NAMES = []
#         if (i + step_size - 1) < f:
#             for j in range(i, i + step_size):
#                 conns.append(get_target(j))
#                 grp_NAMES.append(NAMES[0][j])
#         if len(conns) > 0:
#             points = startgame(conns, grp_NAMES)
#             for point in points:
#                 NAMES[1].append(point)
#             print(NAMES[1])
#     print("All Games played")
#
#
# def startgame(conns, players):
#     grp_players = []
#     for conn, player in zip(conns, players):
#         grp_players.append(Player(player, list(), conn=conn))
#         print('game started for ', player)
#     if len(conns) == 1:
#         grp_players.append(Player('comp1', list(), isBot=True))
#     #     p1 = Player(player,list(),)
#     #     p2 = Player('comp1',list(),isBot=True)
#     env = RummyAgent(grp_players, max_card_length=3, max_turns=20)
#     # Number of games
#     number_of_games = 5
#
#     # Number of rounds
#     number_of_rounds = env.max_turns
#
#     debug = True
#     for _game in range(number_of_games):
#         env.reset(env.players)
#         random.shuffle(env.players)
#         _round = 0
#         print("-" * 50)
#         print("Game Number: {}".format(_game + 1))
#         print("-" * 50)
#         while not env.play():
#             env._update_turn()
#             print("%" * 50)
#             print("Game Number: {} Round Number: {}".format(_game + 1, _round + 1))
#             print("%" * 50)
#             _round += 1
#
#             for player in env.players:
#                 if player.isBot:
#                     if env.play():
#                         continue
#                     if debug:
#                         print(f'{player.name} Plays')
#                     env.computer_play(player)
#                     if debug:
#                         player.get_info(debug)
#                         if player.stash == 0:
#                             print(f'{player.name} wins the round')
#                 else:
#                     if env.play():
#                         continue
#                     round_obs = player.get_info(debug)
#                     json.dumps(round_obs)
#                     # Send The status
#
#                     player.conn.send(str.encode(f'sendinfo'))
#                     player_response = str(player.conn.recv(20480), "utf-8")
#                     print(player_response)
#                     player.conn.send(str.encode(str(round_obs)))
#                     # Wait to receive it
#
#                     ro = str(player.conn.recv(20480), "utf-8")
#                     ro = int(ro)
#                     print(f'Action pick : {ro}')
#                     env.pick_card(player, ro)
#                     print("Send action for card drop")
#                     round_obs = player.get_info(debug)
#                     json.dumps(round_obs)
#                     player.conn.send(str.encode(f'sendaction_for_card_drop'))
#                     ro = str(player.conn.recv(20480), "utf-8")
#                     print(ro)
#                     player.conn.send(str.encode(str(round_obs)))
#                     ro = str(player.conn.recv(20480), "utf-8")
#                     ro = int(ro) % 10
#                     print(f'Action Drop {ro}')
#                     if len(player.stash) == 1:
#                         env.drop_card(player, player.stash[0])
#                     else:
#                         env.drop_card(player, player.stash[ro])
#
#         result = ''
#         for player in env.players:
#             if player.conn != None:
#                 player.conn.send(str.encode('round_over'))
#                 ro = str(player.conn.recv(20480), "utf-8")
#                 print(ro)
#             player.points += player.stash_score()
#             res = f'Player: {player.name}  Score: {player.points} Stash Score : {player.stash_score()}\n'
#             print(res)
#             result += res
#         for player in env.players:
#             if player.conn != None:
#                 player.conn.send(str.encode(result))
#     points = []
#     for _player in env.players:
#         print(f'Name: {_player.name} Score: {_player.points} ')
#     #         if _player.name == player:
#     #             points = _player.points
#     for player in env.players:
#         if player.conn != None:
#             player.conn.send(str.encode('gameover'))
#             points.append(player.points)
#     return points


# %%
create_workers()
create_jobs()
