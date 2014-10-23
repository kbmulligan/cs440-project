'''
Created on Oct 20, 2014

@author: scrhoads

from russell/norvig aima games.py
'''
from utils import argmax, infinity
from game import Game

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
        return state.to_move

    def display(self, state):
        "Print or otherwise display the state."
        print state

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
class Vindinium(MiniMaxGame):
    
    def __init__(self, myHeroName):
        self.myHeroName = myHeroName
    
    def actions(self, state):
        availActions = list()
        
        #put stay in 
        availActions.append((STAY_ACTION))
       
        #parse game object
        game = Game(state, self.myHeroName)
         
        #go over other people's mines, and create actions for those
        for minePos, ownerId in game.others_mines_locs.iteritems():
            availActions.append((ATTACK_TROLL_ACTION, minePos))
            
        #do the same for adversaries
        for opPos, opId in game.other_heroes_locs.iteritems():
            availActions.append((ATTACK_PLAYER_ACTION, opPos, opId))
            
        #actions for health
        for barPos in game.taverns_locs:
            availActions.append((HEAL_ACTION, barPos))
            
        return availActions
                            
    def result(self, state, move):
        
        moveAction = move[0]
        
        if moveAction == STAY_ACTION:
            pass
        elif moveAction == ATTACK_TROLL_ACTION:
            pass
        elif moveAction == ATTACK_PLAYER_ACTION:
            pass
        else:
            #heal
            pass
    
def alphabeta_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = game.to_move(state)

    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = -infinity
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a),
                                 alpha, beta, depth+1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = infinity
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a),
                                 alpha, beta, depth+1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alphabeta_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or
                   (lambda state,depth: depth>d or game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    return argmax(game.actions(state),
                  lambda a: min_value(game.result(state, a),
                                      -infinity, infinity, 0))