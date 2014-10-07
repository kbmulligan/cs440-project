import random
import time
from game import Game, Board

PLAYERS = 4
HERO_IDs = ['1', '2', '3', '4']

dirs = ['Stay', 'North', 'South', 'East', 'West']

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

STEPS_TO_DISPLAY = 9



class Bot:
    pass
    
class NitorBot(Bot):

    identity = 0
    turn = 0
    pos = ()
    life = 0
    gold = 0
    mineCount = 0
    locHistory = []      # list of past coordinates in chronological order, i.e. [0] => start, [-1] => last turn 


    # mode is one of ('WAIT', 'TRAVEL')
    mode = 'WAIT'

    # goal is one of ('EXPAND', 'DEFEND', 'HEAL', 'FIGHT', 'WANDER')
    goal = 'EXPAND'

    # dest is coords of immediate goal destination
    dest = ()
    
    
    # called each turn, updates hero state, returns direction of movement hero bot chooses to go
    def move(self, state):
        t0 = time.time()

        game = Game(state)
        self.update(game)
        
        if (self.turn % 10 == 0):
            print ''
            printMap(game)
            # print game.state
        
        print ''
        print self.summary()

        direction = STAY
        
        self.goal = self.determineGoal(game)
        self.dest = self.determineDest(self.goal, game)


        if self.dest:                                       # Make progress toward destination
            self.mode = TRAVEL
            direction = self.getDirTo(self.dest, game.board)
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

        goal = EXPAND                                       # default goal is to expand

        if (self.life < LIFE_THRESHOLD):                    # healing overrides other goals if necessary
            goal = HEAL

        return goal

    # return destination based on goal
    def determineDest (self, goal, game):
        destination = ()

        if goal == EXPAND:
            mines = self.findNearestObj('mine', game)
            owned = self.getOwnedByID(mines, self.identity, game)
            unowned = [mine for mine in mines if mine not in owned]

            if (unowned):
                destination = unowned[0]

        
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
    def getDirTo(self, dest, board):
        drow = dest[0] - self.pos[0]
        dcol = dest[1] - self.pos[1]

        if (abs(drow) > abs(dcol)):               # if N/S is greater than E/W difference, the make the N/S change first
            if (drow > 0):
                d = SOUTH
            elif (drow < 0):
                d = NORTH
            else:
                d = STAY
        else:
            if (dcol > 0):
                d = EAST
            elif (dcol < 0):
                d = WEST
            else:
                d = STAY

        if not board.passable(board.to(self.pos, d)) and board.to(self.pos, d) != dest:
            d = random.choice(dirs)

        return d

    def setDest(self, newDest):
        self.dest = newDest

    def setGoal(self, newGoal):
        self.goal = newGoal
        
    # update self state vars
    def update(self, game):
        self.turn = game.state['game']['turn'] / PLAYERS
        
        history = self.locHistory
        if (len(history) > STEPS_TO_DISPLAY):
            history = history[-STEPS_TO_DISPLAY:]
        print history
        
        for hero in game.heroes:
            if hero.name == 'nitorbot':
                self.gold = hero.gold
                self.life = hero.life
                self.pos = hero.pos['x'], hero.pos['y']
                self.locHistory.append(self.pos)
                self.mineCount = hero.mineCount
                self.crashed = hero.crashed
                self.identity = hero.id

    def summary(self):
        return 'Turn: ' + str(self.turn) + '  pos: ' + str(self.pos) + '  $: ' + str(self.gold) + \
             '  Life: ' + str(self.life) + '  Mines: ' + str(self.mineCount) + '  Dest: ' + str(self.dest)
        # + '  ID: ' + str(self.identity)
        # + '  Crashed: ' + str(self.crashed)

        
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
                dist = getDistance(position, locs[i], game)
                if (dist < shortestDist):
                    shortestDist = dist
                    closestLoc = tuple(locs[i])
            nearest.append(closestLoc)
            locs.pop(locs.index(closestLoc))

        return nearest

    # given a location (coords) and game state returns the owner hero ID of the location or None if no owner exists
    def getOwnerID(self, loc, game):

        size = game.board.size
        tiles = game.board.tiles

        owner = tiles[loc[0]][loc[1]]
        # owner = '@9'

        ownerID = owner.__repr__()[1]

        if (ownerID not in HERO_IDs):                   # safety check and correction
            ownerID = None
        else:
            ownerID = int(ownerID)

        return ownerID

    # given a list of mines and an ID, returns only those owned by ID
    def getOwnedByID(self, mines, ID, game):
        owned = []
        for mine in mines:
            if (self.getOwnerID(mine, game) == ID):
                owned.append(mine)
        return owned

    


class RandomBot(Bot):
    def move(self, state):
        game = Game(state)
        dirs = ['Stay', 'North', 'South', 'East', 'West']
        return choice(dirs)

class SlowBot(Bot):
    def move(self, state):
        dirs = ['Stay', 'North', 'South', 'East', 'West']
        time.sleep(2)
        return choice(dirs)



########## UTILITY FUNCTIONS ##########

# returns a board line with characters replaced into something readable
def convertLine(line):
    newLine = []

    for item in line:
        if (item == -game.AIR):
            newLine.append('..')
        elif (item == game.WALL):
            newLine.append('XX')
        elif (item == TAVERN):
            newLine.append('00')
        else:
            newLine.append(str(item))

    return newLine

# prints the game's depiction of the board, prints custom view if directed
def printMap(game, customView=False):
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

# given a loc, return locs of all 4 neighboring cells, checks for borders
def getNeighboringLocs(self, loc, board):
    x, y = loc
    locs = []

    above = (x - 1, y)
    below = (x + 1, y)
    left =  (x, y - 1)
    right = (x, y + 1)

    if (x > 0):                 locs.append(above)
    if (x < board.size - 1):    locs.append(below)
    if (y > 0):                 locs.append(left)
    if (y < board.size - 1):    locs.append(right)

    return locs

# returns Manhattan distance from pos1 to pos2 given state 'game'
def getDistance(pos1, pos2, game):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])