'''
Created on Oct 20, 2014

@author: scrhoads

from russell/norvig aima games.py
'''
from utils import argmax, infinity
from game import Game
from math import ceil
from time import time

STAY_ACTION = 'STAY'
ATTACK_TROLL_ACTION = 'ATTACK_TROLL'
ATTACK_PLAYER_ACTION = 'ATTACK_PLAYER'
HEAL_ACTION = 'HEAL'


class MiniMaxGame:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        "Return a list of the allowable moves at this point."
        pass

    def result(self, state, move):
        "Return the state that results from making a move from a state."
        pass

    def utility(self, state, player):
        "Return the value of this final state to player."
        pass

    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        return not self.actions(state)

    def to_move(self, state):
        "Return the player whose move it is in this state."
        pass

    def display(self, state):
        "Print or otherwise display the state."
        print state

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
class Vindinium(MiniMaxGame):
    
    def __init__(self, myHeroName, initialState):
        self.myHeroName = myHeroName
        self.initial = initialState
        
    def to_move(self):
        return self.myHeroName
    
    def actions(self, state):
        availActions = list()
        
        #put stay in 
        #availActions.append((STAY_ACTION,0))
       
        #parse game object
        game = Game(state, self.myHeroName)
         
        #go over other people's mines, and create actions for those
        for minePos, ownerId in game.others_mines_locs.iteritems():
            availActions.append((ATTACK_TROLL_ACTION, minePos))
            
        #do the same for adversaries
        for opPos, opId in game.other_heroes_locs.iteritems():
            availActions.append((ATTACK_PLAYER_ACTION, opPos, opId))
            
        """#actions for health
        for barPos in game.taverns_locs:
            availActions.append((HEAL_ACTION, barPos))
        """
        
        return availActions
                            
    def result(self, state, move):
        
        moveAction = move[0]
        
        #parse state
        game = Game(state, self.myHeroName, False)
        myHeroPos = state['game']['heroes'][game.myHeroId -1]['pos']
        
        if moveAction == STAY_ACTION:
            #result of stay is lose one health, and gain 1 gold per mine owned
            newHealth = game.myHero.life + 1
            newGold = game.myHero.gold + game.myHero.mineCount
            
            #update state
            state['game']['heroes'][game.myHeroId -1]['gold'] = newGold
            state['game']['heroes'][game.myHeroId -1]['life'] = newHealth
            
        elif moveAction == ATTACK_TROLL_ACTION:
            #get troll pos
            trollPos = move[1]
            
            #calculate number of moves to location
            numMoves = self.calculateNumberOfMoves((myHeroPos['x'], myHeroPos['y']), trollPos)
            
            #adjust health for fight with troll
            newLife = game.myHero.life - 20
            newGold = game.myHero.gold
            newMines = game.myHero.mineCount
            
            if newLife > 0:
                #victory increase # mines and gold 
                newMines = newMines + 1
                newGold = newGold + newMines
            else:
                #died fighting troll
                #life and mineCount go to zero
                newLife = 0
                newMines = 0
                
            #update state
            state['game']['heroes'][game.myHeroId -1]['gold'] = newGold
            state['game']['heroes'][game.myHeroId -1]['mineCount'] = newMines
            state['game']['heroes'][game.myHeroId -1]['life'] = newLife
            state['game']['heroes'][game.myHeroId -1]['pos']['x'] = trollPos[0]
            state['game']['heroes'][game.myHeroId -1]['pos']['y'] = trollPos[1]
            
            
        elif moveAction == ATTACK_PLAYER_ACTION:
            
            playerPos = move[1]
            playerId = int(move[2])
            
            #calculate number of moves to location
            numMoves = self.calculateNumberOfMoves((myHeroPos['x'], myHeroPos['y']), playerPos)
            
            #adjust health for trip
            lifeAfterMoves = game.myHero.life - numMoves
            
            #adjust health for fight with troll
            newLife = 0
            newMines = game.myHero.mineCount
            newGold = game.myHero.gold
           
            playerHealth = state['game']['heroes'][playerId -1]['life']
            
            if lifeAfterMoves <= 20 or lifeAfterMoves < playerHealth:
                #assume hero dies if starting life is 20 or less
                #or if his life is less than opponent
                newLife = 0

            elif lifeAfterMoves > playerHealth:
                #our hero has > 20 health and greater than player, should win battle
                #this calculation isn't totally accurate. doesn't take into account if myHero
                #attacks first. this is more conservative
                newLife = lifeAfterMoves - ceil(playerHealth/20.0) * 20
                
            #claim the mines if hero won    
            if newLife > 0:
                #incr. num mines by how many were taken from other player
                addtlMineIfWonFight = state['game']['heroes'][game.myHeroId -1]['mineCount']
                newMines = newMines + addtlMineIfWonFight
                
                #addtl gold for being alive at end of turn
                newGold = newGold + newMines
                
            else:
                #lost life and all the mines
                newLife = 0
                newMines = 0
                
            #update state
            state['game']['heroes'][game.myHeroId -1]['gold'] = newGold
            state['game']['heroes'][game.myHeroId -1]['mineCount'] = newMines
            state['game']['heroes'][game.myHeroId -1]['life'] = newLife
            state['game']['heroes'][game.myHeroId -1]['pos']['x'] = playerPos[0]
            state['game']['heroes'][game.myHeroId -1]['pos']['y'] = playerPos[1]
            
        else:
            #heal
            barPos = move[1]
            
            movesToBar = self.calculateNumberOfMoves((myHeroPos['x'], myHeroPos['y']), barPos)
            
            lifeAfterMove = game.myHero.life - movesToBar
            
            if lifeAfterMove < 1:
                #can't have neg. health or die from traveling
                lifeAfterMove = 1
                
            #pay and do the heal
            newGold = game.myHero.gold - 2
            newLife = lifeAfterMove + 50
            
            #make sure we don't have > 100 health
            if newLife > 100:
                newLife = 100
                
            #update state
            state['game']['heroes'][game.myHeroId -1]['gold'] = newGold
            state['game']['heroes'][game.myHeroId -1]['life'] = newLife
            state['game']['heroes'][game.myHeroId -1]['pos']['x'] = barPos[0]
            state['game']['heroes'][game.myHeroId -1]['pos']['y'] = barPos[1]
            
        return state
    
    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        #terminal state going to be on a per life basis initially
        retVal = False
        
        game = Game(state, self.myHeroName)
        
        #if myHero's life is 0 or less, it's a terminal state
        if game.myHero.life <= 0:
            retVal = True
            
        return retVal
    
    def utility(self, state, player):
        "Return the value of this final state to player."
        #value is going to be the amount of utility
        
        game = Game(state, self.myHeroName)
        
        utility = 0
        
        for hero in game.heroes:
            if hero.name == player:
                utility = hero.gold
                #add amount of life to utility
                utility = utility + hero.life
                break;
        return utility
    
    def calculateNumberOfMoves(self, curPos, destPos):
        #this is the number of moves assuming no obstacles
        xDiff = abs(curPos[0] - destPos[0])
        yDiff = abs(curPos[1] - destPos[1])
        
        totalNumMoves = xDiff + yDiff
        
        return totalNumMoves
        
        
    
def alphabeta_search(miniMaxGame, d=4, cutoff_test=None, eval_fn=None):
    """Search miniMaxGame to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = miniMaxGame.myHeroName
    state = miniMaxGame.initial

    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = -infinity
        for a in miniMaxGame.actions(state):
            v = max(v, min_value(miniMaxGame.result(state, a),
                                 alpha, beta, depth+1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = infinity
        for a in miniMaxGame.actions(state):
            v = min(v, max_value(miniMaxGame.result(state, a),
                                 alpha, beta, depth+1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alphabeta_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or
                   (lambda state,depth: depth>d or miniMaxGame.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: miniMaxGame.utility(state, player))
    return argmax(miniMaxGame.actions(state),
                  lambda a: min_value(miniMaxGame.result(state, a),
                                      -infinity, infinity, 0))