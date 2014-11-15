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

# determine gold value of loc based on game state (turn, gold leaders, health, etc)
def gold_value(loc, game):

    if (loc in game.mines_locs):
        val = get_mine_value(loc)
    elif (loc in game.heroes_locs):
        val = get_hero_value(loc)        
    
    return val
    
def get_mine_value(loc):
    val = 0
    return val

def get_hero_value(loc):
    val = 0
    return val
    
def get_mine_count(hero_id, game):
    mc = 0
    mine_counts = [(h.id, h.mineCount) for h in game.heroes]
    for x in mine_counts:
        if hero_id == x[0]:
            mc = x[1]
    return mc