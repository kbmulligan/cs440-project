#################################################
# pathfinder.py - Vindinium bot A* pathfinding
# by Stephen Rhoads
#    Brett Mulligan
# Oct 2014
# CSU CS440
# Dr. Asa Ben-Hur
#################################################

from game import Game, Board, MineTile, HeroTile
from priorityqueue import PriorityQueue

VERBOSE_ASTAR = False

PLAYERS = 4
HERO_IDs = ['1', '2', '3', '4']

dirs = ['Stay', 'North', 'South', 'East', 'West']

NORTH = 'North'
SOUTH = 'South'
EAST = 'East'
WEST = 'West'
STAY = 'Stay'

WAIT = 'WAIT'
TRAVEL = 'TRAVEL'

# for A*
MOVE_COST = 1
MOVE_PENALTY = {'SPAWN POINT': 10, 
                'ENEMY': 5, 
                'ADJ ENEMY':3,
                'PROHIBITED': 100}

                
########## UTILITY FUNCTIONS ##########

# returns Manhattan distance from pos1 to pos2
def get_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

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

    
class Pathfinder():

    # use A* to find the shortest path between two points
    # returns list of coords from start to end, not including start
    # disregards heroes in the way
    # cost_estimate is a heuristic function that takes only start and
    # end locations as arguments
    def get_path(self, start, end, board, cost_estimate=get_distance):

        explored = set()
        previous = {}
        previous[start] = None
        moves = {}
        moves[start] = 0

        frontier = PriorityQueue()
        frontier.insert(start, cost_estimate(start, end))

        if VERBOSE_ASTAR: print 'get_path start, end:', start, end

        while not frontier.is_empty():

            if VERBOSE_ASTAR: print 'get_path frontier:', frontier

            current = frontier.remove()
            explored.add(current)

            if VERBOSE_ASTAR: print 'get_path explored set', explored
            if VERBOSE_ASTAR: print 'get_path current pos:', current

            if (current == end):
                if VERBOSE_ASTAR: print 'Found end loc'
                break
            else:
                neighbors = get_neighboring_locs(current, board)

                if VERBOSE_ASTAR: print 'get_path neighbors:', neighbors

                for n in neighbors:
                    if n not in explored and (board.passable(n) or n in (start, end)):
                        moves[n] = moves[current] + MOVE_COST
                        frontier.insert(n, cost_estimate(n, end) + moves[n])
                        previous[n] = current

        # found goal, now reconstruct path
        i = end
        path = [i]
        while i != start:
            if (i in previous):
                path.append(previous[i])
                i = previous[i]
            else:
                print 'get_path error: probably could not find a valid path from', start, 'to', end
                path = [start, start]           # return something valid
                break

        path.reverse()

        return path

    # returns the length of the path in moves
    def path_cost(self, path):
        return len(path) - 1

    # cost estimate for A*, Manhattan distance heuristic
    def path_heuristic(self, n, end):
        return get_distance(n, end) + self.penalties(n)

    # returns heuristic adjustments for walking over things like spawn points or bots with high relative life
    def penalties(self, pos):
        total = 0

        board = self.knowledge['GAME'].board
        enemy_locs = [x for x in self.knowledge['GAME'].heroes_locs if x != self.pos]
        enemy_spawns = self.knowledge['ENEMY SPAWNS']

        if pos in enemy_spawns:
            total += MOVE_PENALTY['SPAWN POINT']

        if pos in enemy_locs:
            total += MOVE_PENALTY['ENEMY']

        adj_hero = []
        for loc in enemy_locs:
            for here in get_neighboring_locs(loc, board):
                adj_hero.append(here)

        if pos in adj_hero:
            total += MOVE_PENALTY['ADJ ENEMY']

        if self.loc_history[-20:].count(pos) > 5:
            total += MOVE_PENALTY['PROHIBITED']

        unpassable = [x for x in get_neighboring_locs(pos, board) if not board.passable(x)]
        total += len(unpassable)

        return total

    

    

