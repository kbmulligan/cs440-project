'''
bot.py - Vindinium bot AI
@author: kbmulligan, scrhoads
Oct 2014
CSU CS440
Dr. Asa Ben-Hur
'''

import random
import time
import sys
import math
from game import Game, Board, MineTile, HeroTile
from priorityqueue import PriorityQueue
import pathfinder
import compare
from minimax import Vindinium, HEAL_ACTION, \
    multiplayer_minimax_search

BOT_NAME = 'rambot'

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
MIN_LIFE = 21
FULL_LIFE = 100

COMFORTABLE_LEAD = 200          # raw gold lead wanted before going defensive
DESIRED_LEAD_MARGIN = 1.0       # percentage lead wanted before going defensive
MIN_LEAD_MARGIN = 0.9
NEVER_STOP = 100000

BEER_COST = 2
BEER_LIFE = 50
MIN_MINES_TO_COMPARE = 4
MAX_MINES_TO_COMPARE = 10
CENTER_MASS_WEIGHT = 0.5
TERRIBLE_SCORE = -1000

ENEMIES_TO_COMPARE = 4

WAYPOINTS = 1


# for A*
MOVE_COST = 1
MOVE_PENALTY = {'SPAWN POINT': 3, 
                'ENEMY': 5, 
                'ADJ ENEMY':3,
                'PROHIBITED': 100}
MAX_SEARCHES = 5

# for custom map printout
AIR_TILE = '  '
WALL_TILE = '##'
TAVERN_TILE = '[]'

# output board frames
game_output = 'lastgame.vin'

class Bot:
    identity = 0
    globalTurn = 0
    turn = 0
    pos = ()
    life = 0
    gold = 0
    mineCount = 0
    moves = {}
    
class RamBot(Bot):

    loc_history = []         # list of past coordinates in chronological order, i.e. [0] => start, [-1] => last turn
    deaths = 0
    hub = 0

    knowledge = {}          # A dict with misc info in it. 
                            # Keys used so far: 
                            #   'GAME'
                            #   'ENEMY SPAWNS'
                            #   'LEADER'

    # mode is one of ('WAIT', 'TRAVEL')
    mode = 'WAIT'

    # goal is one of ('EXPAND', 'DEFEND', 'HEAL', 'FIGHT', 'WANDER')
    goal = ('EXPAND')

    # waypoints is list of coords of planned destinations, waypoints[0] is next immediate destination
    waypoints = []

    def __init__(self, name=BOT_NAME):
        self.spawn = None
        self.name = name
        self.pf = pathfinder.Pathfinder()
        self.moves[STAY] = 0
        self.moves[NORTH] = 0
        self.moves[SOUTH] = 0
        self.moves[EAST] = 0
        self.moves[WEST] = 0
        self.lastAction = None
    
    # called each turn, updates hero state, returns direction of movement hero bot chooses to go
    def move(self, state):
        """Determine which way the bot should move given game state."""
        
        ##### ADMIN AND GAME MANAGEMENT #############################
        t0 = time.time()
        
        myId = state['hero']['id']

        game = Game(state, myId) 
        
        if self.turn < 2:
            self.game_setup(game)
        
        self.update(game)

        # print game info
        if (self.turn % SHOW_MAP_EVERY_X_TURNS == 0):
            print ''
            print pretty_map(game, SHOW_CUSTOM_MAP)

        write_gamestate(state)
        print self.summary()
        ##### ADMIN COMPLETE - START WORKING ACTUAL MOVEMENT ########
        
        direction = None
        
        #reeval goal every time
        self.goal = self.determine_goal(game, state)
        print "executing goal: " + str(self.goal)
        
        #clear all waypoints
        self.remove_all_waypoints()
       
        if self.goal[0] == HEAL:
            
            self.add_waypoint(self.determine_dest(HEAL, game)[0])
            
        else:
            self.add_waypoint((self.goal[1][0], self.goal[1][1]))
        
        if self.get_current_waypoint():
            #TODO see brett's calculation for when to heal
            #if health is low, go heal
            """if game.myHero.life < 30:
                self.remove_all_waypoints()
                self.add_waypoint(self.determine_dest(HEAL, game))
            """
            self.mode = TRAVEL

            path = self.pf.get_path(self.pos, self.get_current_waypoint(), game.board, self.path_heuristic)
            
            #make sure we have a valid path, if not revert to heal
            while (path == [self.pos, self.pos]) and self.goal != DEFEND:
                self.remove_current_waypoint()
                
                self.add_waypoint(self.determine_dest(HEAL, game, randomness=True)[0])
                
                path = self.pf.get_path(self.pos, self.get_current_waypoint(), game.board, self.path_heuristic)
                
            
        ###self.evaluate_waypoints()   # This version seems to do well
        

        """
        # Make progress toward destination
        if any(self.waypoints):
            wpt = self.get_current_waypoint()
            path = self.pf.get_path(self.pos, wpt, game.board, self.path_heuristic)
        else:
            print 'No waypoints!!!'
            path = [self.pos, self.pos]
        
        # if no valid path found, remove waypoint, add randomness, and try again
        searches = 1
        while (path == [self.pos, self.pos]):
            self.remove_current_waypoint()
            if not self.waypoints:
                self.add_waypoints(self.determine_dest(self.goal, game, randomness=True))
            next_wpt = self.get_current_waypoint()
            path = self.pf.get_path(self.pos, next_wpt, game.board, self.path_heuristic)
            searches += 1
            if searches > MAX_SEARCHES:
                path = [self.pos, self.pos]
                break
        """

        print 'Current path:', path
        print 'Distance:', len(path) - 1
        
        if len(path) > 1: 
            next_pos = path[1]
        else:
            next_pos = self.pos
        print 'Next move:', next_pos

        direction = self.pf.get_dir_to(self.pos, next_pos)
        print 'Direction:', direction

        # test if bot has arrived at waypoint
        #if game.board.to(self.pos, direction) == self.get_current_waypoint():
        #    self.remove_current_waypoint()


        ##### MORE INFORMATION AND TIME/GAME MANAGEMENT #############
        print ''
        # self.print_comparison_tests(game)

        # Safety check -- I think bad dirs can cause HTTP 400 Errors - kbm
        direction = safety_check(direction)
        self.record_move(direction)                         # track all moves
        
        td = time.time() - t0                               # Time check
        if (td > TIME_THRESHOLD):
            print "Close on time!!!", td
        print 'Response time: %.3f' % td
        
        return direction

    def print_comparison_tests(self, game):
        print 'Comparisons...'
        # print 'Minecounts:'
        # print '1:', compare.get_mine_count(1, game)
        # print '2:', compare.get_mine_count(2, game)
        # print '3:', compare.get_mine_count(3, game)
        # print '4:', compare.get_mine_count(4, game)
        
        # for hero_loc in game.heroes_locs:
            # print hero_loc, compare.get_hero_value(hero_loc, game)
        
        if STAY in self.moves: print 'STAY\'s:', self.moves[STAY]

        order = compare.project_end_state(game)
        print 'Projected final order:', order
        
        print 'Hero', order[0], 'will win by:', compare.project_gold_diff(order[0], order[1], game), 'gold'
        
        # print 'Top 5 Targets by Value:' 
        for target in compare.highest_value_targets(game, 4):
            if target in game.other_heroes_locs and target != self.pos:
                print 'Hero', target
            else:
                print 'Mine', target
        
        return
    
    # returns goal based on game state
    def determine_goal (self, game, state):
        goal = None

        goal = (EXPAND,0)                                       # default
        
        order = compare.project_end_state(game)
        
        desired_lead_margin = (DESIRED_LEAD_MARGIN - MIN_LEAD_MARGIN) * \
            compare.turns_left(game)/(game.state['game']['maxTurns']/PLAYERS) + MIN_LEAD_MARGIN
        if (compare.projected_winner(game) == self.identity and \
                compare.project_gold_diff(order[0], order[1], game) > \
                compare.project_end_gold(game.get_hero_by_id(self.identity), game) \
                * desired_lead_margin + NEVER_STOP):
            goal = (DEFEND,self.pos)

#         life_threshold = (LIFE_THRESHOLD - MIN_LIFE) / (order.index(self.identity) + 1) + MIN_LIFE
        life_threshold = 40
        if (self.life < life_threshold and self.can_buy(1)  or 
            (self.lastAction != None and self.lastAction[0] == HEAL_ACTION and self.life < 80)):                             # healing override
            goal = (HEAL,0)
        
        """
        targets = compare.highest_value_targets(game, ENEMIES_TO_COMPARE)               # grab all targets
        hero_targets = [x for x in targets if x in game.heroes_locs and x != self.pos]  # filter for heroes
        if hero_targets:
            target = hero_targets[0]                                                    # select most valuable
            enemy_life = game.other_heroes_locs[target]
            if (self.life > enemy_life):
                goal = FIGHT
        """
        if goal[0] == EXPAND:
            #don't come in here if we already set to heal or defend
            miniMax = Vindinium(game.myHeroName, state)
            #         miniAction = alphabeta_search(miniMax, d=1)
          
            #default depth 
            d = 1 

            #determine depth of search based off of board size or # of taverns
            if state['game']['board']['size'] > 18 or len(game.taverns_locs) > 20:
                #only look at our player
                d = 0
            
            #send to max finder
            goal = multiplayer_minimax_search(miniMax, d=d)
            
        self.lastAction = goal
        
        return goal

    # return destination based on goal
    def determine_dest (self, goal, game, randomness=False):
        destination = []

        if goal == EXPAND:
            destination.append(self.select_mine(game, randomness))
        
        if goal == DEFEND:
            destination.append(self.pos)

        if goal == HEAL:
            if randomness:
                destination.append(random.choice(self.find_nearest_obj('tavern', game)))
            else:
                nearestTavernLoc = self.find_nearest_obj('tavern', game)[0]
                
                destination.append(nearestTavernLoc)
                
            """
            if self.life + BEER_LIFE - get_distance(self.pos, destination[0]) < FULL_LIFE:
                destination.append(destination[0])
                print destination
            """
            
        if goal == FIGHT:
            targets = compare.highest_value_targets(game, ENEMIES_TO_COMPARE)
            marks = [x for x in targets if x in game.heroes_locs and x != self.pos]
            if marks:
                destination.append(marks[0])
            else:
                destination.append(self.find_nearest_obj('enemy', game)[0])

        return destination
        
    def select_mine(self, game, randomness=False):
        nearest = self.find_nearest_unowned_mines(game, mines_to_compare(game))
        print 'near mines', nearest
        if not nearest:
            self.goal = DEFEND
            goal = DEFEND
            dest = self.pos
        elif randomness:
            dest = random.choice(nearest)
        else:
            dest = self.choose_best(nearest)
        return dest
    
    # configure and optimize waypoints based on goal/health
    def evaluate_waypoints(self):
        self.goal = self.determine_goal(self.knowledge['GAME'])
        while len(self.waypoints) < WAYPOINTS:
            self.add_waypoints(self.determine_dest(self.goal, self.knowledge['GAME']))

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
    
    def add_waypoints(self, wpts):
        for wpt in wpts:
            self.add_waypoint(wpt)

    def insert_immediate_waypoint(self, wpt):
        self.waypoints.insert(0, wpt)

    def set_goal(self, newGoal):
        self.goal = newGoal

    def life_threshold(self, game):
        order = compare.project_end_state(game)
        return (LIFE_THRESHOLD - MIN_LIFE) / (order.index(self.identity) + 1) + MIN_LIFE
    
    def healthy(self):
        return self.life > self.life_threshold(self.knowledge['GAME'])

    def missing_life(self):
        return FULL_LIFE - self.life

    def can_buy(self, beers):
        return self.gold >= BEER_COST * beers
        
    # update self state vars
    def update(self, game):
        self.turn = game.state['game']['turn'] / PLAYERS + 1
        self.globalTurn = game.state['game']['turn']
        
        for hero in game.heroes:
            if hero.name == self.name:
                self.gold = hero.gold
                self.life = hero.life
                self.pos = hero.pos['x'], hero.pos['y']
                self.loc_history.append(self.pos)
                self.mineCount = hero.mineCount
                self.crashed = hero.crashed
                self.identity = hero.id
                
                #kick out of loop after finding your own info - sr
                break

        if self.just_died():
            self.deaths += 1
            self.remove_all_waypoints()
        
        self.knowledge['GAME'] = game
        self.knowledge['LEADER'] = game.get_leader_id()

        mines = self.find_nearest_obj('mine', game)
        control_pts = self.get_owned_by_id(mines, self.identity, game)
        control_pts.append(self.spawn)
        self.hub = compare.center_mass(control_pts)

    def summary(self):
        history = self.loc_history
        if (len(history) > STEPS_TO_DISPLAY):
            history = history[-STEPS_TO_DISPLAY:]
        # print 'History:', history

        return 'Id: ' + str(self.identity) + ' Turn: ' + str(self.turn) + '/' + str(self.globalTurn) + '  pos: ' + str(self.pos) + \
            '  $: ' + str(self.gold) + '  Life: ' + str(self.life) + \
            '  Mines: ' + str(self.mineCount) + \
            '  Mode: ' + str(self.goal) + \
            '  Dest: ' + str(self.get_current_waypoint()) + \
            '  Deaths: ' + str(self.deaths) + \
            '\nHistory: ' + str(history) + \
            '\nWpts: ' + str(self.waypoints)

            # + '  ID: ' + str(self.identity)
            # + '  Crashed: ' + str(self.crashed)
            # + '  Dest: ' + str(self.get_current_waypoint()) + \
            
    def record_move(self, dir):
        self.moves[dir] += 1

    def just_died(self):
        died = False
        if (len(self.loc_history) > 1):
            died = get_distance(self.loc_history[-1], self.loc_history[-2]) > 1
        return died

    def choose_best(self, locs):
        best = None
        q = PriorityQueue()

        print 'choose best, locs:', locs
        
        if locs != None:
            for loc in locs:
                q.insert(loc, -self.score_loc(loc))     # by highest score
            best = q.remove()

        print 'choose best, best:', best

        return best

    def score_loc(self, loc):
        score = 0
        board = self.knowledge['GAME'].board
        
        gold_value = compare.gold_value(loc, self.knowledge['GAME'])
        path = self.pf.get_path(self.pos, loc, board, self.path_heuristic)
        if (path == [self.pos, self.pos]):
            return TERRIBLE_SCORE
        path_length = len(path) - 1
        
        # self.hub is the middle of all owned mines and spawn point
        if self.hub:
            dhub = get_distance(self.hub, loc)
        else:
            dhub = 0
            
        # total score accounts for time taken to capture and normalizes for that same cost
        # this essential leaves you with future value per move spent, optimizing the use of each move
        score += (float(gold_value) - path_length) / path_length
        score -= float(dhub) * CENTER_MASS_WEIGHT
        
        print 'Score', loc, ' val:', gold_value, 'path len:', path_length, 'dCenter:', dhub, '  Score:', score
        return score


    # returns list of locs sorted by path length (A*)
    def nearest_by_path(self, locs):
        nearest = []
        for x in range(len(locs)):
            closest_loc = ()
            shortest_dist = sys.maxint

            for i in range(len(locs)):
                dist = len(self.pf.get_path(self.pos, locs[i], self.knowledge['GAME'].board, self.path_heuristic))
                if (dist < shortest_dist):
                    shortest_dist = dist
                    closest_loc = tuple(locs[i])
            nearest.append(closest_loc)
            locs.pop(locs.index(closest_loc))
        return nearest


    def find_nearest_unowned_mines(self, game, num):
        mines = self.find_nearest_obj('mine', game)
        owned = self.get_owned_by_id(mines, self.identity, game)
        unowned = [mine for mine in mines if mine not in owned]

        if (unowned):
            unowned_mines = unowned[:num]
        else:
            unowned_mines = None

        return unowned_mines
        
    def get_owned_mines(self, game):
        mines = self.find_nearest_obj('mine', game)
        owned = self.get_owned_by_id(mines, self.identity, game)
        return owned

    # returns list of positions of nearest 'obj' (from player) in state 'game' 
    # sorted from nearest to farthest (Manhattan)
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

    # returns list of locations sorted in ascending path_distance from 'position'
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
        x = 0
        y = 0
        for hero in game.heroes:
            if hero.name == self.name:
                self.spawn = hero.spawn
                x = int(hero.spawn['x'])
                y = int(hero.spawn['y'])
                break

        spawns = [hero.spawn for hero in game.heroes]
        spawns = [s for s in spawns if s != self.spawn]
        self.knowledge['ENEMY SPAWNS'] = spawns
        
        self.spawn = (x,y)            # final assignment should be usable numbers
        return None
    

    # cost estimate for A*, Manhattan distance heuristic
    def path_heuristic(self, n, end):
        return get_distance(n, end) + self.penalties(n)

    # returns heuristic adjustments for walking over things like spawn points or bots with high relative life
    def penalties(self, pos):
        total = 0

        board = self.knowledge['GAME'].board
        enemy_locs = self.knowledge['GAME'].other_heroes_locs.keys()
        enemy_spawns = self.knowledge['ENEMY SPAWNS']

        if pos in enemy_spawns:
            total += MOVE_PENALTY['SPAWN POINT']
            
        return total
        
    def game_setup(self, game):
        erase_file()
        self.determine_spawns(game)

        
        
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

def mines_to_compare(game):
    return min([max([int(math.ceil(len(game.mines_locs) * 0.4)), MIN_MINES_TO_COMPARE])], MAX_MINES_TO_COMPARE)

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
                output += game.state['game']['board']['tiles'][begin:end] + '\n'
            
        return output

# writes game state to file readable by vinvis if desired
def write_gamestate(state):
    f = open(game_output, 'a')
    if f == None:
        print 'error opening output file', game_output
    else:
        size = state['game']['board']['size']
        board = []
        output = ''
        for i in range(size):
            begin = i * size*2
            end = begin + size*2
            output += state['game']['board']['tiles'][begin:end] + '\n'
        f.write(output)
        f.write('\n')
        
    f.close()
    return
    
def erase_file():
    f = open(game_output, 'w')
    if f == None:
        print 'error opening output file', game_output
    else:
        f.truncate(0)
    f.close()
        
# returns Manhattan distance from pos1 to pos2
def get_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
def safety_check(dir):
    direction = dir
    if dir not in [NORTH, SOUTH, EAST, WEST]:
        print 'Direction was None or invalid!!!'
        direction = STAY
    return direction

