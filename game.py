import re
from time import time

TAVERN = 0
AIR = -1
WALL = -2

PLAYER1 = 1
PLAYER2 = 2
PLAYER3 = 3
PLAYER4 = 4

AIM = {'North': (-1, 0),
       'East': (0, 1),
       'South': (1, 0),
       'West': (0, -1),
       'Stay': (0, 0)}

class HeroTile:
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '@' + str(self.id)

class MineTile:
    def __init__(self, heroId = None):
        self.heroId = heroId

    def __repr__(self):
        return 'M' + str(self.heroId)

class Game:
    def __init__(self, state, myHeroId, parseBoard=True):
        
        self.turn = state['game']['turn']
        self.maxTurns = state['game']['maxTurns']
        
        self.heroes = [Hero(state['game']['heroes'][i]) for i in range(len(state['game']['heroes']))]
       
        self.myHeroId = myHeroId 
        self.myHeroName = None
        self.myHero = None 
        
        self.heroes_locs = {}
        self.other_heroes_locs = {}
        
        #get my heroid
        for hero in self.heroes:
            #setup all hero locations
#             self.heroes_locs[(hero.pos['y'], hero.pos['x'])] = hero.id

            if hero.id == myHeroId:
                self.myHeroName = hero.name
                self.myHero = hero
            else:
                #populate other_heroes_loc
#                 self.other_heroes_locs[(hero.pos['y'], hero.pos['x'])] = hero.id
                pass
        
        if parseBoard:
            startParse = time()

            self.board = Board(state['game']['board'])
            self.mines_locs = {}
            self.others_mines_locs={}
            
            
            
            state['game']['board']['mines'] = {}
            state['game']['board']['taverns'] = []

            self.taverns_locs = set([])
            for row in range(len(self.board.tiles)):
                for col in range(len(self.board.tiles[row])):
                    obj = self.board.tiles[row][col]
                    if isinstance(obj, MineTile):
                        self.mines_locs[(row, col)] = obj.heroId
                        
                        #if not mine, add to 'others' list
                        if obj.heroId != str(self.myHeroId):
                            self.others_mines_locs[(row,col)] = obj.heroId
                        
                        state['game']['board']['mines'][(row, col)] = obj.heroId
                    
                    elif (obj == TAVERN):
                        self.taverns_locs.add((row, col))
                        state['game']['board']['taverns'].append((row, col))

#                     """
                    elif isinstance(obj, HeroTile):
                        self.heroes_locs[(row, col)] = obj.id
                        
                        #if not me, add to others list
                        if obj.id != str(self.myHeroId):
                            self.other_heroes_locs[(row,col)] = obj.id
#                     """
            
            endParse = time() - startParse
            print "parseTime: " + str(endParse)
                        
        
        self.state = state
                    
    def get_leader_id(self):
        maxId = 1
        maxGold = -1
        
        for hero in self.heroes:
            if hero.gold > maxGold:
                maxId = hero.id
                maxGold = hero.gold
                
        return maxId
        
    def get_hero_by_id(self, hero_id):
        wanted = None
        for hero in self.heroes:
            if hero_id == hero.id:
                wanted = hero
                break
        return wanted
        

class Board:
    def __parseTile(self, string):
        if (string == '  '):
            return AIR
        if (string == '##'):
            return WALL
        if (string == '[]'):
            return TAVERN
        match = re.match('\$([-0-9])', string)
        if (match):
            return MineTile(match.group(1))
        match = re.match('\@([0-9])', string)
        if (match):
            return HeroTile(match.group(1))

    def __parseTiles(self, tiles):
        vector = [tiles[i:i+2] for i in range(0, len(tiles), 2)]
        matrix = [vector[i:i+self.size] for i in range(0, len(vector), self.size)]

        return [[self.__parseTile(x) for x in xs] for xs in matrix]

    def __init__(self, board):
        self.size = board['size']
        self.tiles = self.__parseTiles(board['tiles'])

    def passable(self, loc):
        """True if bot can walk through."""
        x, y = loc
        pos = self.tiles[x][y]
        return (pos != WALL) and (pos != TAVERN) and not isinstance(pos, MineTile) and not isinstance(pos, HeroTile)

    def passables(self, locs):
        return [x for x in locs if (self.passable(x))]

    def to(self, loc, direction):
        'calculate a new location given the direction'
        row, col = loc
        d_row, d_col = AIM[direction]
        n_row = row + d_row
        if (n_row < 0): n_row = 0
        if (n_row > self.size): n_row = self.size
        n_col = col + d_col
        if (n_col < 0): n_col = 0
        if (n_col > self.size): n_col = self.size

        return (n_row, n_col)



class Hero:
    def __init__(self, hero):
        self.name = hero['name']
        self.pos = hero['pos']
        self.life = hero['life']
        self.gold = hero['gold']
        self.mineCount = hero['mineCount']
        self.crashed = hero['crashed']
        self.id = hero['id']
        self.spawn = hero['spawnPos']

