#################################################
# pathfinder.py - Vindinium bot A* pathfinding
# by Stephen Rhoads
#    Brett Mulligan
# Oct 2014
# CSU CS440
# Dr. Asa Ben-Hur
#################################################

import time
from game import Game, Board, MineTile, HeroTile
from priorityqueue import PriorityQueue

VERBOSE_ASTAR = False

PATHFINDER_TIMEOUT = 0.15

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
    
        t0 = time.time()

        explored = set()
        previous = {}
        previous[start] = None
        moves = {}
        moves[start] = 0

        frontier = PriorityQueue()
        frontier.insert(start, cost_estimate(start, end))

        if VERBOSE_ASTAR: print 'get_path start, end:', start, end

        while not frontier.is_empty():
        
            if (time.time() - t0 > PATHFINDER_TIMEOUT):
                print 'PATHFINDING TIMEOUT: Averting disconnect...'
                print '    get_path: Probably could not find a valid path from', start, 'to', end
                return [start, start] 

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
                return [start, start]    # return something valid

        path.reverse()

        return path
        
    # returns direction to go based on start and destination coords
    def get_dir_to(self, start, dest):
        drow = dest[0] - start[0]
        dcol = dest[1] - start[1]

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

    # returns the length of the path in moves
    def path_cost(self, path):
        return len(path) - 1



    

