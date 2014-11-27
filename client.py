#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import time
from bot import RandomBot, SlowBot, RamBot, ManualBot

TIMEOUT=15
MAP = 'm4'

vfName = 'viewgames.html'

def get_new_game_state(session, server_url, key, mode='training', number_of_turns = 10, mapx=MAP):
    """Get a JSON from the server containing the current state of the game"""

    if(mode=='training'):
        #Don't pass the 'map' parameter if you want a random map
        params = { 'key': key, 'turns': number_of_turns, 'map': mapx}
        api_endpoint = '/api/training'
    elif(mode=='arena'):
        params = { 'key': key}
        api_endpoint = '/api/arena'

    #Wait for 10 minutes
    r = session.post(server_url + api_endpoint, params, timeout=10*60)

    if(r.status_code == 200):
        return r.json()
    else:
        print("Error when creating the game")
        print(r.text)

def move(session, url, direction):
    """Send a move to the server
    
    Moves can be one of: 'Stay', 'North', 'South', 'East', 'West' 
    """

    try:
        r = session.post(url, {'dir': direction}, timeout=TIMEOUT)

        if(r.status_code == 200):
            return r.json()
        else:
            print("Error HTTP %d\n%s\n" % (r.status_code, r.text))
            print r.text
            return {'game': {'finished': True}}
    except requests.exceptions.RequestException as e:
        print(e)
        return {'game': {'finished': True}}


def is_finished(state):
    return state['game']['finished']

def start(server_url, key, mode, turns, bot, use_map=MAP):
    """Starts a game with all the required parameters"""

    # Create a requests session that will be used throughout the game
    session = requests.session()

    if(mode=='arena'):
        print(u'Connected and waiting for other players to join...')
    # Get the initial state
    state = get_new_game_state(session, server_url, key, mode, turns, use_map)
    print("Playing at: " + state['viewUrl'])
    viewURL = state['viewUrl']
    
    print ("init game state: " + str(state))

    recordURL(viewURL, mode)

    while not is_finished(state):
        # Some nice output ;)
        sys.stdout.write('.')
        sys.stdout.flush()

        # Choose a move
        direction = bot.move(state)

        # Send the move and receive the updated game state
        url = state['playUrl']
        state = move(session, url, direction)

    # Clean up the session
    session.close()
    
    return viewURL


def recordURL(viewUrl, mode):
    vf = open(vfName, 'r+')
    data = []
        
    if (vf == None):
        print('Error opening file: ', vf)
    else:
        if (mode == 'training'):
            map_name = MAP.upper()
        else:
            map_name = 'ARENA'

        data.append('<p>' + time.asctime() + '  <a href="' + viewUrl + '">' + map_name + '</a></p>\n')
        
        for line in vf:
            data.append(line)

        vf.seek(0)

        for line in data:
            vf.write(line)

        vf.close()


if __name__ == "__main__":
    if (len(sys.argv) < 4):
        print("Usage: %s <key> <publicName> <[training|arena]> <number-of-games|number-of-turns> [server-url]" % (sys.argv[0]))
        print('Example: %s mySecretKey myBotName training 20' % (sys.argv[0]))
    else:
        key = sys.argv[1]
        botName = sys.argv[2]
        mode = sys.argv[3]

        if(mode == "training"):
            number_of_games = 1
            number_of_turns = int(sys.argv[4])
        else: 
            number_of_games = int(sys.argv[4])
            number_of_turns = 300 # Ignored in arena mode

        if(len(sys.argv) == 6):
            server_url = sys.argv[5]
        else:
            server_url = "http://vindinium.org"
            
        if (len(sys.argv) == 7):
            use_map = sys.argv[6]

        for i in range(number_of_games):
            viewURL = start(server_url, key, mode, number_of_turns, RamBot(botName), use_map=MAP)
            print("\nGame finished: %d/%d" % (i+1, number_of_games))
            
        
