from random import choice
import time
from game import Game

PLAYERS = 4

NORTH = 'North'
SOUTH = 'South'
EAST = 'East'
WEST = 'West'
STAY = 'Stay'

HEAL = 'HEAL'
EXPAND = 'EXPAND'
DEFEND = 'DEFEND'
FIGHT = 'FIGHT'
WANDER = 'WANDER'

WAIT = 'WAIT'
TRAVEL = 'TRAVEL'

TIME_THRESHOLD = 0.9

LIFE_THRESHOLD = 80



class Bot:
    pass
    
class NitorBot(Bot):

    turn = 0
    pos = ()
    life = 0
    gold = 0
    mineCount = 0


    # mode is one of ('WAIT', 'TRAVEL')
    mode = 'WAIT'

    # goal is one of ('EXPAND', 'DEFEND', 'HEAL', 'FIGHT', 'WANDER')
    goal = 'EXPAND'

    # dest is coords of immediate goal destination
    dest = ()
    
    
    # called each turn, updates hero state, returns direction of movement herobot chooses to go
    def move(self, state):
        t0 = time.time()

        game = Game(state)
        self.update(game)
        
        dirs = ['Stay', 'North', 'South', 'East', 'West']

        if (self.turn % 10 == 0):
            print ''
            self.printMap(game, True)
            # print game.state
        
        print ''
        print self.summary()

        direction = STAY
        
        self.goal = self.determineGoal(game)
        self.setDest(self.determineDest(self.goal, game))


        if self.dest:                                       # Make progress toward destination
            self.mode = TRAVEL
            direction = self.getDirTo(self.dest)
            print direction
        
        else:
            self.mode = WAIT


        if direction == None:                               # Safety check -- I believe bad directions can cause HTTP 400 Errors - kbm
            direction = STAY

        td = time.time() - t0                               # Time check
        if (td > TIME_THRESHOLD):
            print "Close on time!!!", td

        return direction

    # returns goal based on game state
    def determineGoal (self, game):
        goal = None

        goal = EXPAND

        if (self.life < LIFE_THRESHOLD):
            goal = HEAL


        return goal

    # return destination based on goal
    def determineDest (self, goal, game):
        destination = ()

        if goal == EXPAND:
            destination = self.findNearestObj('mine', game)[0]
        
        elif goal == DEFEND:
            destination = None

        elif goal == HEAL:
            destination = self.findNearestObj('tavern', game)[0]

        elif goal == FIGHT:
            destination = None

        else:
            destination = None

        return destination

    # returns direction to go based on destination coords 'dest'
    def getDirTo(self, dest):
        drow = dest[0] - self.pos[0]
        dcol = dest[1] - self.pos[1]

        if (drow > 0):
            d = SOUTH
        elif (drow < 0):
            d = NORTH
        else:
            d = STAY

        if (dcol > 0):
            d = EAST
        elif (dcol < 0):
            d = WEST

        return d

    def setDest(self, newDest):
        self.dest = newDest
        
    # update self state vars
    def update(self, game):
        self.turn = game.state['game']['turn'] / PLAYERS
        
        for hero in game.heroes:
            if hero.name == 'nitorbot':
                self.gold = hero.gold
                self.life = hero.life
                self.pos = hero.pos['x'], hero.pos['y']
                self.mineCount = hero.mineCount
                self.crashed = hero.crashed

    def summary(self):
        return 'Turn: ' + str(self.turn) + '  pos: ' + str(self.pos) + '  $: ' + str(self.gold) + \
        '  Life: ' + str(self.life) + '  Mines: ' + str(self.mineCount) + '  Dest: ' + str(self.dest) + '  Crashed: ' + str(self.crashed)

    def printMap(self, game, customView=False):
        if customView:
            for line in game.board.tiles:
                print ''.join(convertLine(line))
        else:
            size = game.state['game']['board']['size']
            board = []
            for i in range(size):
                begin = i*size*2
                end = begin + size*2
                board.append(game.state['game']['board']['tiles'][begin:end])
            
            for line in board:
                print line

        
    # returns list of positions of nearest 'obj' (from player) in state 'game' sorted from nearest to farthest
    def findNearestObj(self, obj, game):
        nearest = []
        
        if (obj == 'mine'):
            nearest = self.findNearestLocFromPos(self.pos, game.mines_locs.keys(), game)
  
        elif (obj == 'tavern'):
            nearest = self.findNearestLocFromPos(self.pos, game.taverns_locs, game)

        elif (obj == 'enemy'):
            notimplemented

        else:
            pass
        
        return nearest

    # returns list of locations sorted in ascending distance from 'position'
    def findNearestLocFromPos(self, position, locations, game):
        locs = list(locations)
        nearest = []

        for x in range(len(locs)):
            closestLoc = ()
            shortestDist = game.board.size * 2

            for i in range(len(locs)):
                dist = self.getDistance(position, locs[i], game)
                if (dist < shortestDist):
                    shortestDist = dist
                    closestLoc = tuple(locs[i])
            nearest.append(closestLoc)
            locs.pop(locs.index(closestLoc))

        return nearest
        
    # returns Manhattan distance from pos1 to pos2 given state 'game'
    def getDistance(self, pos1, pos2, game):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    
class RandomBot(Bot):

    def move(self, state):
        game = Game(state)
        dirs = ['Stay', 'North', 'South', 'East', 'West']
        return choice(dirs)

class FighterBot(Bot):
    def move(self, state):
        dirs = ['Stay', 'North', 'South', 'East', 'West']
        return choice(dirs)

class SlowBot(Bot):
    def move(self, state):
        dirs = ['Stay', 'North', 'South', 'East', 'West']
        time.sleep(2)
        return choice(dirs)



########## UTILITY FUNCTIONS ##########

def convertLine(line):
    newLine = []

    for item in line:
        if (item == -1):
            newLine.append('..')
        elif (item == -2):
            newLine.append('XX')
        elif (item == 0):
            newLine.append('00')
        else:
            newLine.append(str(item))

    return newLine