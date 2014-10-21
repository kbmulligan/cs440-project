#################################################
# bot.py - Vindinium bot move AI
# by Stephen Rhoads
#    Brett Mulligan
# Oct 2014
# CSU CS440
# Dr. Asa Ben-Hur
#################################################

import random
import time
from game import Game, Board, MineTile, HeroTile
from priorityqueue import PriorityQueue

BOT_NAME = 'nitorbot'

VERBOSE_ASTAR = False
SHOW_CUSTOM_MAP = True
SHOW_MAP_EVERY_X_TURNS = 1

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
STEPS_TO_DISPLAY = 7


LIFE_THRESHOLD = 70
FULL_LIFE = 100

BEER_COST = 2

MINES_TO_COMPARE = 3


# for A*
MOVE_COST = 1

# for custom map printout
AIR_TILE = '  '
WALL_TILE = '##'
TAVERN_TILE = '[]'


class Bot:
    identity = 0
    turn = 0
    pos = ()
    life = 0
    gold = 0
    mineCount = 0
    
class RamBot(Bot):

    loc_history = []         # list of past coordinates in chronological order, i.e. [0] => start, [-1] => last turn
    deaths = 0

    knowledge = {}          # A dict with misc info in it. 
                            # Keys used so far: 
                            #   'ENEMY SPAWNS'
                            #   'LEADER'

    # mode is one of ('WAIT', 'TRAVEL')
    mode = 'WAIT'

    # goal is one of ('EXPAND', 'DEFEND', 'HEAL', 'FIGHT', 'WANDER')
    goal = 'EXPAND'

    # waypoints is list of coords of planned destinations, waypoints[0] is next immediate destination
    waypoints = []
    
    def __init__(self, name=BOT_NAME):
        self.spawn = None
        self.name = name
    
    
    # called each turn, updates hero state, returns direction of movement hero bot chooses to go
    def move(self, state):
        t0 = time.time()

        game = Game(state)
        self.update(game)

        if self.turn <= 1:
            self.determine_spawns(game)

        # print game info
        if (self.turn % SHOW_MAP_EVERY_X_TURNS == 0):
            print ''
            print pretty_map(game, SHOW_CUSTOM_MAP)

        print self.summary()

        self.eval_nearby(game)

        # Make progress toward destination or re-evaulate destination/goal
        direction = None
        if self.get_current_waypoint():
            
            self.mode = TRAVEL

            path = get_path(self.pos, self.get_current_waypoint(), game.board)
            print 'Current path:', path
            print 'Distance:', len(path) - 1
            
            next_pos = path[1]
            print 'Next move:', next_pos

            direction = self.get_dir_to(next_pos)
            print 'Direction:', direction

            if game.board.to(self.pos, direction) == self.get_current_waypoint():
                self.remove_current_waypoint()
        
        else:
            self.goal = self.determine_goal(game)
            self.add_waypoint(self.determine_dest(self.goal, game))


        # Safety check -- I think bad dirs can cause HTTP 400 Errors - kbm
        if direction == None:    
            direction = STAY

        td = time.time() - t0                               # Time check
        if (td > TIME_THRESHOLD):
            print "Close on time!!!", td

        return direction

    # returns goal based on game state
    def determine_goal (self, game):
        goal = None

        goal = EXPAND                                       # default

        if (self.life < LIFE_THRESHOLD and self.can_buy()): # healing override
            goal = HEAL

        return goal

    # return destination based on goal
    def determine_dest (self, goal, game):
        destination = ()

        if goal == EXPAND:
            nearest_mines = self.find_nearest_unowned_mines(game, MINES_TO_COMPARE)
            destination = self.choose_best(nearest_mines)
        
        elif goal == DEFEND:
            destination = None

        elif goal == HEAL:
            destination = self.find_nearest_obj('tavern', game)[0]

        elif goal == FIGHT:
            destination = None

        else:
            destination = None

        return destination

    def eval_nearby(self, game):
        mine = self.choose_best(self.find_nearest_unowned_mines(game, MINES_TO_COMPARE))
        if (self.life + path_cost(get_path(self.pos, mine, game.board))*2 > 85 and \
            mine not in self.waypoints):
            self.insert_immediate_waypoint(mine)
        
        near_tavern = self.find_nearest_obj('tavern', game)[0]  
        if (self.missing_life() > path_cost(get_path(self.pos, near_tavern, game.board))*2 and \
            near_tavern not in self.waypoints and self.can_buy()):
            self.insert_immediate_waypoint(near_tavern)

    def get_current_waypoint(self):
        wpt = None
        if any(self.waypoints):
            wpt = self.waypoints[0]
        return wpt

    def remove_current_waypoint(self):
        if any(self.waypoints):
            self.waypoints.pop(0)

    def remove_all_waypoints(self):
        self.waypoints = []

    def add_waypoint(self, wpt):
        self.waypoints.append(wpt)

    def insert_immediate_waypoint(self, wpt):
        self.waypoints.insert(0, wpt)

    

    # returns direction to go based on destination coords 'dest'
    def get_dir_to(self, dest):
        drow = dest[0] - self.pos[0]
        dcol = dest[1] - self.pos[1]

        # if N/S is greater than E/W difference, the make the N/S change first
        if (abs(drow) > abs(dcol)):               
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

        return d

    def set_goal(self, newGoal):
        self.goal = newGoal

    def healthy(self):
        return self.life > LIFE_THRESHOLD

    def missing_life(self):
        return FULL_LIFE - self.life

    def can_buy(self):
        return self.gold >= BEER_COST
        
    # update self state vars
    def update(self, game):
        self.turn = game.state['game']['turn'] / PLAYERS
        
        for hero in game.heroes:
            if hero.name == self.name:
                self.gold = hero.gold
                self.life = hero.life
                self.pos = hero.pos['x'], hero.pos['y']
                self.loc_history.append(self.pos)
                self.mineCount = hero.mineCount
                self.crashed = hero.crashed
                self.identity = hero.id

        if self.just_died():
            self.deaths += 1
            self.remove_all_waypoints()
        
        self.knowledge['GAME'] = game
        self.knowledge['LEADER'] = game.get_leader_id()



    def just_died(self):
        died = False
        if (len(self.loc_history) > 1):
            died = get_distance(self.loc_history[-1], self.loc_history[-2]) > 1
        return died

    def summary(self):
        history = self.loc_history
        if (len(history) > STEPS_TO_DISPLAY):
            history = history[-STEPS_TO_DISPLAY:]
        # print 'History:', history

        return 'Turn: ' + str(self.turn) + '  pos: ' + str(self.pos) + \
            '  $: ' + str(self.gold) + '  Life: ' + str(self.life) + \
            '  Mines: ' + str(self.mineCount) + \
            '  Dest: ' + str(self.get_current_waypoint()) + \
            '  Deaths: ' + str(self.deaths) + \
            '\nHistory: ' + str(history) + \
            '\nWpts: ' + str(self.waypoints)

            # + '  ID: ' + str(self.identity)
            # + '  Crashed: ' + str(self.crashed)


    def choose_best(self, locs):
        best = None
        if (locs):
            for loc in locs:
                if self.get_owner_id(loc, self.knowledge['GAME']) == self.knowledge['LEADER']:
                    best = loc
                else:
                    if best == None:
                        best = locs[0]
        return best

    def find_nearest_unowned_mines(self, game, num):
        mines = self.find_nearest_obj('mine', game)
        owned = self.get_owned_by_id(mines, self.identity, game)
        unowned = [mine for mine in mines if mine not in owned]

        if (unowned):
            unowned_mines = unowned[:num]
        else:
            unowned_mines = None

        return unowned_mines

    # returns list of positions of nearest 'obj' (from player) in state 'game' 
    # sorted from nearest to farthest
    def find_nearest_obj(self, obj, game):
        nearest = []
        
        if (obj == 'mine'):
            nearest = self.find_nearest_loc_from(self.pos, game.mines_locs.keys(), game)
        elif (obj == 'tavern'):
            nearest = self.find_nearest_loc_from(self.pos, game.taverns_locs, game)
        elif (obj == 'enemy'):
            nearest = self.find_nearest_loc_from(self.pos, game.heroes_locs.keys(), game)
        else:
            nearest = None
            print 'find_nearest_obj: invalid obj'
        return nearest

    # returns list of locations sorted in ascending distance from 'position'
    def find_nearest_loc_from(self, position, locations, game):
        locs = list(locations)
        nearest = []

        for x in range(len(locs)):
            closestLoc = ()
            shortestDist = game.board.size * 2

            for i in range(len(locs)):
                dist = get_distance(position, locs[i])
                if (dist < shortestDist):
                    shortestDist = dist
                    closestLoc = tuple(locs[i])
            nearest.append(closestLoc)
            locs.pop(locs.index(closestLoc))

        return nearest

    # given a location (coords) and game state, returns the owner hero ID of 
    # the location or None if no owner exists
    def get_owner_id(self, loc, game):

        size = game.board.size
        tiles = game.board.tiles

        owner = tiles[loc[0]][loc[1]]
        ownerID = owner.__repr__()[1]

        if (ownerID not in HERO_IDs):             # safety check and correction
            ownerID = None
        else:
            ownerID = int(ownerID)
        return ownerID

    # given a list of mines and an ID, returns only those owned by ID
    def get_owned_by_id(self, mines, ID, game):
        owned = []
        for mine in mines:
            if (self.get_owner_id(mine, game) == ID):
                owned.append(mine)
        return owned

    # return a tuple of enemy locs
    def get_enemy_locations(self, game):
        locs = [x for x in game.heroes_locs.keys() if x != self.pos]
        return locs

    def determine_spawns(self, game):

        for hero in game.heroes:
            if hero.name == self.name:
                self.spawn = hero.spawn

        spawns = [hero.spawn for hero in game.heroes]
        spawns = [x for x in spawns if x != self.spawn]
        self.knowledge['ENEMY SPAWNS'] = spawns

        return None

    

########## STOCK BOTS #################
# Useful for testing and troubleshooting
class RandomBot(Bot):
    def move(self, state):
        game = Game(state)
        dirs = ['Stay', 'North', 'South', 'East', 'West']
#         return choice(dirs)

class SlowBot(Bot):
    def move(self, state):
        dirs = ['Stay', 'North', 'South', 'East', 'West']
        time.sleep(2)
#         return choice(dirs)

class ManualBot(Bot):                                        # Could not resist
    def move(self, state):
        print pretty_map(Game(state))
        return self.to_dir(raw_input())

    def to_dir(self, letter):
        if (letter == 'w'):
            direction = NORTH
        elif (letter == 's'):
            direction = SOUTH
        elif (letter == 'a'):
            direction = WEST
        elif (letter == 'd'):
            direction = EAST
        else:
            direction = STAY
        return direction


########## UTILITY FUNCTIONS ##########

# returns a board line with characters replaced into something readable
def convert_line(line):
    newLine = []

    TAVERN = 0
    AIR = -1
    WALL = -2

    for item in line:
        if (item == AIR):
            newLine.append(AIR_TILE)
        elif (item == WALL):
            newLine.append(WALL_TILE)
        elif (item == TAVERN):
            newLine.append(TAVERN_TILE)
        else:
            newLine.append(str(item))

    return newLine

# prints the game's depiction of the board, prints custom view if directed
def pretty_map(game, customView=False):
        output = ''

        if customView:
            columns = range(len(game.board.tiles))
            columns = [str(x) for x in columns]
            columns = [' ' + x if int(x) < 10 else x for x in columns ]
            output += '   ' + ''.join(columns) + '\n'

            row = 0
            for line in game.board.tiles:
                srow = str(row)
                if int(srow) < 10: srow = ' ' + srow
                output += srow + ' ' + ''.join(convert_line(line)) + '\n'
                row += 1

        else:
            size = game.state['game']['board']['size']
            board = []
            for i in range(size):
                begin = i * size*2
                end = begin + size*2
                board.append(game.state['game']['board']['tiles'][begin:end])
            
            for line in board:
                print line

        return output
                

# given a loc, return locs of all 4 neighboring cells, checks for borders
def get_neighboring_locs(loc, board):
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

# returns Manhattan distance from pos1 to pos2
def get_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# returns heuristic adjustments for walking over things like spawn points or bots with high relative life
def penalties(pos, board):
    total = 0


    return total

# cost estimate for A*, Manhattan distance heuristic
def cost_estimate(n, end, board):
    return get_distance(n, end) + penalties(n, board)




# use A* to find the shortest path between two points
# returns list of coords from start to end, not including start
# disregards heroes in the way
def get_path(start, end, board):

    explored = set()
    previous = {}
    previous[start] = None
    moves = {}
    moves[start] = 0

    frontier = PriorityQueue()
    frontier.insert(start, cost_estimate(start, end, board))

    if VERBOSE_ASTAR: print 'get_path start, end:', start, end

    while not frontier.is_empty():

        if VERBOSE_ASTAR: print 'get_path frontier:', frontier

        current = frontier.remove()
        explored.add(current)

        if VERBOSE_ASTAR: print 'get_path explored', explored

        if VERBOSE_ASTAR: print 'get_path current:', current

        if (current == end):
            if VERBOSE_ASTAR: print 'Found end loc'
            break
        else:
            neighbors = get_neighboring_locs(current, board)

            if VERBOSE_ASTAR: print 'get_path neighbors:', neighbors

            for n in neighbors:
                if n not in explored and (board.passable(n) or n in (start, end)):
                    moves[n] = moves[current] + MOVE_COST
                    frontier.insert(n, cost_estimate(n, end, board) + moves[n])
                    previous[n] = current

    # found goal, now reconstruct path
    i = end
    path = [i]
    while i != start:
        path.append(previous[i])
        i = previous[i]

    path.reverse()

    return path

# returns the length of the path in moves
def path_cost(path):
    return len(path) - 1