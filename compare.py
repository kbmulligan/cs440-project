#################################################
# compare.py - Vindinium comparisons find equivalent gold values
# by Stephen Rhoads
#    Brett Mulligan
# Oct 2014
# CSU CS440
# Dr. Asa Ben-Hur
#################################################

import game
import pathfinder
import priorityqueue as pq

BOTS = 4

def highest_value_locs(game):
    q = pq.PriorityQueue()
    
    for mloc in game.others_mines_locs:
        q.insert(mloc, -gold_value(mloc, game))
    
    for hloc in game.other_heroes_locs:
        q.insert(hloc, -gold_value(hloc, game))
    
    locs = []
    while not q.is_empty():
        locs.append(q.remove())
    
    return locs

# determine gold value of loc based on game state (turn, gold leaders, health, etc)
def gold_value(loc, game):

    if (loc in game.mines_locs):
        val = get_mine_value(loc, game)
    elif (loc in game.heroes_locs):
        val = get_hero_value(loc, game)        
    else:
        val = 0
        
    return val
    
def get_mine_value(loc, game):
    val = turns_left(game)
    return val

def get_hero_value(loc, game):
    val = 0
    val = get_mine_count(int(game.heroes_locs[loc]), game)
    val *= turns_left(game)
    return val
    
def get_mine_count(hero_id, game):
    mc = 0
    mine_counts = [(h.id, h.mineCount) for h in game.heroes]
    for x in mine_counts:
        if hero_id == x[0]:
            mc = x[1]
    return mc
    
def turns_left(game):
    return (game.state['game']['maxTurns']/BOTS - game.state['game']['turn']/BOTS)

# returns projected (at last turn) list of hero id's ordered from richest to poorest, given current game state
def project_end_state(game):
    order = pq.PriorityQueue()
    
    for hero in game.heroes:
        riches = hero.gold + hero.mineCount * turns_left(game)
        order.insert(hero.id, -riches)
    
    final = []
    while not order.is_empty():
        final.append(order.remove())
    
    return final
    
def projected_winner(game):
    return project_end_state(game)[0]