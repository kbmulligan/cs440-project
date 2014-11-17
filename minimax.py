'''
Created on Oct 20, 2014

@author: scrhoads

from russell/norvig aima games.py
'''
from utils import argmax, infinity
from game import Game
from math import ceil, log
from time import time
from copy import deepcopy

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
    
    def actions(self, state, parseBoard=False):
        availActions = list()
        
        #put stay in 
        #availActions.append((STAY_ACTION,0))
        
        #get id for who's turn it is
        globalTurn = state['game']['turn']
        
        playerId = (globalTurn % 4) 
        playerName = state['game']['heroes'][playerId ]['name']
        
        #parse game object and get moves for other chars
        game = Game(state, playerName, parseBoard)
         
        #go over other people's mines, and create actions for those
#         for minePos, ownerId in game.others_mines_locs.iteritems():
        for minePos, ownerId in game.state['game']['board']['mines'].iteritems():
            if ownerId != str(playerId + 1):
                availActions.append((ATTACK_TROLL_ACTION, minePos, ownerId))
        """    
        #do the same for adversaries
#         for opPos, opId in game.other_heroes_locs.iteritems():
        for hero in game.state['game']['heroes']:
            if hero['id'] != (playerId + 1):
                availActions.append((ATTACK_PLAYER_ACTION, (hero['pos']['y'], hero['pos']['x']), hero['id']))
        """    
        """#actions for health
        for barPos in game.taverns_locs:
            availActions.append((HEAL_ACTION, barPos))
        """
        
        return availActions
                            
    def result(self, initState, move):
        
        state = deepcopy(initState)
        
        
        #store this move in game.lastAction
        state['game']['lastAction'] = str(move)
        
        moveAction = move[0]
        
        #get id for who's turn it is
        globalTurn = state['game']['turn']
        playerId = (globalTurn % 4) 
        playerName = state['game']['heroes'][playerId ]['name']
        
        #save this palyer's name for utility calc
        state['game']['lastPlayer'] = playerName
        state['game']['lastPlayerZeroId'] = playerId
        
        #parse state
        game = Game(state, playerName, False)
        myHeroPos = state['game']['heroes'][playerId]['pos']
        
        numMoves = 0
        
        if moveAction == STAY_ACTION:
            #result of stay is lose one health, and gain 1 gold per mine owned
            newHealth = game.myHero.life + 1
            newGold = game.myHero.gold + game.myHero.mineCount
            
            #update state
            state['game']['heroes'][playerId]['gold'] = newGold
            state['game']['heroes'][playerId]['life'] = newHealth
            
        elif moveAction == ATTACK_TROLL_ACTION:
            #get troll pos
            trollPos = move[1]
            ownerId = move[2]
            
            #calculate number of moves to location
            numMoves = self.calculateNumberOfMoves((myHeroPos['y'], myHeroPos['x']), trollPos)
            
            #adjust health for fight with troll and trip
            newLife = game.myHero.life - 20 - 5 #5 is a hard coded number to take into account moves from health fill up to fight
            newMines = game.myHero.mineCount

            #account for gold earned on the trip there
            newGold = game.myHero.gold + (numMoves * newMines)
            
            if newLife > 0:
                #victory increase # mines and gold 
                newMines = newMines + 1
                newGold = newGold + newMines
                
                #update owner's minecount, if previously owned
                if str(ownerId) != '-':
                    ownerIdInt = int(ownerId)
                    state['game']['heroes'][ownerIdInt - 1]['mineCount'] = state['game']['heroes'][ownerIdInt - 1]['mineCount'] -1  
                    
                #change owner in
                state['game']['board']['mines'][trollPos] = str(playerId + 1)
                
            else:
                #died fighting troll
                #life and mineCount go to zero
                newLife = 0
                newMines = 0
                
            #update state
            state['game']['heroes'][playerId]['gold'] = newGold
            state['game']['heroes'][playerId]['mineCount'] = newMines
            state['game']['heroes'][playerId]['life'] = newLife
            state['game']['heroes'][playerId]['pos']['y'] = trollPos[0]
            state['game']['heroes'][playerId]['pos']['x'] = trollPos[1]
            
            #TODO change map value
            
            
        elif moveAction == ATTACK_PLAYER_ACTION:
            
            playerPos = move[1]
            opponentId = int(move[2])
            
            #calculate number of moves to location
            numMoves = self.calculateNumberOfMoves((myHeroPos['y'], myHeroPos['x']), playerPos)
           
            #min number of moves is 1
            if numMoves == 0:
                numMoves = 1
            
            lifeAfterMoves = game.myHero.life - numMoves
            
            newLife = 0
            newMines = game.myHero.mineCount
            
            #assuming we survive the trip there, we get numMoves*numMines gold
            newGold = game.myHero.gold + (numMoves * int(state['game']['heroes'][playerId]['mineCount']))
           
            oppenentHealth = state['game']['heroes'][opponentId - 1]['life']
            
#             if lifeAfterMoves <= 20 or lifeAfterMoves < oppenentHealth:
            if lifeAfterMoves < oppenentHealth:
                #assume hero dies if starting life is 20 or less
                #or if his life is less than opponent
                newLife = 0

            elif lifeAfterMoves > oppenentHealth:
                #our hero has > 20 health and greater than player, should win battle
                #this calculation isn't totally accurate. doesn't take into account if myHero
                #attacks first. this is more conservative
                newLife = lifeAfterMoves - ceil(oppenentHealth/20.0) * 20
                
            #claim the mines if hero won    
            if newLife > 0:
                #incr. num mines by how many were taken from other player
                addtlMineIfWonFight = state['game']['heroes'][opponentId - 1]['mineCount']
                newMines = newMines + addtlMineIfWonFight
                
                #addtl gold for being alive at end of turn
                newGold = newGold + newMines

                #set their mine count to 0
                state['game']['heroes'][opponentId - 1]['mineCount'] = 0
                
                #move our position to their location
                state['game']['heroes'][game.myHeroId -1]['pos']['y'] = playerPos[0]
                state['game']['heroes'][game.myHeroId -1]['pos']['x'] = playerPos[1]
                
            else:
                #lost life and all the mines
                newLife = 0
                newMines = 0
                
                #give player our mines
                state['game']['heroes'][opponentId - 1]['mineCount'] = state['game']['heroes'][opponentId - 1]['mineCount'] + game.myHero.mineCount
                
                #move back to respawn
                state['game']['heroes'][game.myHeroId -1]['pos']['x'] = state['game']['heroes'][game.myHeroId -1]['spawnPos']['x'] 
                state['game']['heroes'][game.myHeroId -1]['pos']['y'] = state['game']['heroes'][game.myHeroId -1]['spawnPos']['y']
                
            #update state
            state['game']['heroes'][game.myHeroId -1]['gold'] = newGold
            state['game']['heroes'][game.myHeroId -1]['mineCount'] = newMines
            state['game']['heroes'][game.myHeroId -1]['life'] = newLife
            
            
        else:
            #heal
            barPos = move[1]
            
            movesToBar = self.calculateNumberOfMoves((myHeroPos['y'], myHeroPos['x']), barPos)
            
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
            
        #update gold for all other heroes in game
        for hero in game.heroes:
            if hero.id != game.myHeroId:
                state['game']['heroes'][hero.id - 1]['gold'] = (hero.gold + hero.mineCount)
        
        #update numMoves
        try:     
            state['game']['heroes'][game.myHeroId -1]['numMoves'] = state['game']['heroes'][game.myHeroId -1]['numMoves'] + numMoves
        except:
            state['game']['heroes'][game.myHeroId -1]['numMoves'] = numMoves
        
        #update turn count
        state['game']['turn'] = globalTurn + 1
            
        return state
    
    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        #terminal state going to be when turn# == maxTurns
        retVal = False
        
        game = Game(state, self.myHeroName, parseBoard=False)
        
        #if myHero's life is 0 or less, it's a terminal state
        if game.state['game']['finished'] == "True":
            retVal = True
            
        return retVal
    
    def utility(self, state):
        "Return the value of this final state to player."
        #value is going to be the amount of utility
        
#         game = Game(state, self.myHeroName, parseBoard=False)
        
#         if game.myHero.life <= 0:
#             utility = -infinity
#         else:

        playerId = -1
        
        #get player name based off of 
        playerName = state['game']['lastPlayer']
            
        othersGoldCount = []
        for hero in state['game']['heroes']:
            if hero['name'] != playerName:
                othersGoldCount.append(hero['gold'])
                #add amount of life to utility
            else:
                #get this player's id
                playerId = int(hero['id'])
                
        oppenentsGoldSum = sum(othersGoldCount)
       
        numMovesToGetHere = state['game']['heroes'][playerId -1 ]['numMoves']
        
        reduceMoves = 0
        
        if numMovesToGetHere != 0:
            reduceMoves = log(int(numMovesToGetHere))
        
        utility = (state['game']['heroes'][playerId -1]['gold'] - oppenentsGoldSum) - reduceMoves
#         utility = utility * -1
        return utility
    
    def calculateNumberOfMoves(self, curPos, destPos):
        #this is the number of moves assuming no obstacles
        yDiff = abs(curPos[0] - destPos[0])
        xDiff = abs(curPos[1] - destPos[1])
        
        totalNumMoves = xDiff + yDiff
        
        return totalNumMoves
    
def pretty_map(game):
        output = ''

        size = game.state['game']['board']['size']
        for i in range(size):
            begin = i * size*2
            end = begin + size*2
            output += game.state['game']['board']['tiles'][begin:end] + '\n'

        return output
        
        
    
def alphabeta_search(miniMaxGame, d=4, cutoff_test=None, eval_fn=None):
    """Search miniMaxGame to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = miniMaxGame.myHeroName
    initialState = miniMaxGame.initial
#     state = miniMaxGame.initial

    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            evalVal = eval_fn(state) 
            return evalVal
        v = -infinity
        actionList = miniMaxGame.actions(state)
        for a in actionList:
            newState = miniMaxGame.result(state, a)
            v = max(v, min_value(newState, alpha, beta, depth+1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            evalVal = eval_fn(state) 
            return evalVal
        v = infinity
        actionList = miniMaxGame.actions(state) 
        for a in actionList:
            newState = miniMaxGame.result(state, a)
            v = min(v, max_value(newState, alpha, beta, depth+1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v
    
    def getZeroBasedPlayerIdForThisTurn(state):
        
        globalTurn = state['game']['turn']
        playerId = (globalTurn % 4) 
        
        return playerId
    
    def getOurPlayerId(state):
        
        return int(state['hero']['id'])
        
    
    def argMaxMinVal(action):
        newState = miniMaxGame.result(initialState, action)
#         print "action : " + str(action) + "'s result:"
#         print pretty_map(Game(newState, miniMaxGame.myHeroName))
#         minVal = max_value(newState, -infinity, infinity, 0)
        minVal = min_value(newState, -infinity, infinity, 0)
        
        return minVal

    # Body of alphabeta_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or
                   (lambda state,depth: depth>d or miniMaxGame.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: miniMaxGame.utility(state))
    
    actionList = miniMaxGame.actions(miniMaxGame.initial, True)
    print "actionList: " + str(actionList)
#     return argmax(actionList,
#                   lambda a: min_value(miniMaxGame.result(miniMaxGame.initial, a),
#                                       -infinity, infinity, 0))
    maxArg = argmax(actionList, argMaxMinVal)
    return maxArg
    