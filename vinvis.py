# vinvis.py - custom Vindinium game viewer
# -optional
# -requires pygame
# Author: KBM
# Date: Nov 2014
#
# WTFPL
import sys
import math
import random
import re
import pygame
from pygame.locals import *

# main program config
debug = True
paused = True
mute = False
res = (1366, 768) # resolution
borderWidth = 10
bottomPad = 2
fps = 60
title = 'vinvis'
timeInc = 0.4 # seconds
turns = 0
turn = 0

vfn = "lastgame.vin"

BLOCK_WIDTH = 25

next_turn_event = pygame.USEREVENT

# player startup values
startingPoints = 0
startingLives = 5

# color presets
red = pygame.Color(255,0,0)
green = pygame.Color(0,255,0)
blue = pygame.Color(0,0,255)
lightBlue = pygame.Color(200,200,255)
white = pygame.Color(255,255,255)
black = pygame.Color(0,0,0)
teal = pygame.Color(0,255,255)
yellow = pygame.Color(255,255,0)
brown = pygame.Color(100,50,0)

def gray (val):
    return pygame.Color(val,val,val)
    
def recip (heading):
    return (heading + 180) % 360 

def distance (a, b):
    return math.sqrt(abs(a[0] - b[0])**2 + abs(a[1] - b[1])**2)
    
# Class defs
class Player:

    def __init__(self, pts, level):

        self.pts = pts
        self.level = level

    pts = 0
    level = 0
    lives = startingLives

    def getPoints(self):
        return self.pts

    def addPoints(self, newPoints):
        self.pts += newPoints

    def setPoints(self, newPoints):
        self.pts = newPoints

    def takeLife(self):
        self.lives -= 1

    def setLives(self, newLives):
        self.lives = newLives

    def getLives(self):
        return self.lives

    def addLife(self):
        self.lives += 1
    
class Game:

    level = 0

    def __init__(self):
        level = 1

    def setLevel(self, lvl):
        self.level = lvl

    def getLevel(self):
        return self.level
        
# setup

pygame.init()
fpsClock = pygame.time.Clock()

windowSurfObj = pygame.display.set_mode(res, pygame.FULLSCREEN)
pygame.display.set_caption(title)


fontSize = 24
fontObj = pygame.font.Font(pygame.font.get_default_font(), fontSize)
fontObj = pygame.font.SysFont('Courier New', fontSize)
label = 'Status: '
msg = 'Program started...'

# top level game state
game = Game()
game.setLevel(1)
player = Player(0,1)



# input section
def processInput():
    global paused, mute, msg, debug
    
    global lead
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == MOUSEMOTION:
            if not paused:
                pass
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                leftClick(event.pos)
            elif event.button == 2:
                middleClick(event.pos)
            elif event.button == 3:
                rightClick(event.pos)
            elif event.button == 4:
                scrollUp()
            elif event.button == 5:
                scrollDown()
                
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
            elif event.key == K_p:
                paused = not paused
            elif event.key == K_n:
                nextLevel()
            elif event.key == K_d:
                debug = not debug
            elif event.key == K_m or event.key == K_s:
                mute = not mute
            elif event.key == K_SPACE:
                togglePause()

def pollInputs():

    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        if not paused:
            keyLeft()
    elif keys[K_RIGHT]:
        if not paused:
            keyRight()
    if keys[K_UP]:
        if not paused:
            keyUp()     
    elif keys[K_DOWN]:
        if not paused:
            keyDown()

def leftClick(pos):
    global msg, lead
    msg = 'left click'
    next_turn()

def rightClick(pos):
    global msg
    msg = 'right click'
    previous_turn()

def middleClick(pos):
    global msg
    msg = 'middle click'  

def scrollUp():
    global msg, lead
    msg = 'scroll up'
    
def scrollDown():
    global msg, lead
    msg = 'scroll down'
    
def keyLeft():
    global msg, lead
    msg = 'key left'
    
def keyRight():
    global msg, lead
    msg = 'key right'
    
def keyUp():
    global msg, lead
    msg = 'key up'
    
def keyDown():
    global msg, lead
    msg = 'key down'
       
def togglePause():
    global paused
    paused = not paused
    
    if paused:
        pygame.time.set_timer(next_turn_event, 0)
    else:
        pygame.time.set_timer(next_turn_event, int(timeInc*1000))
    
def next_turn():
    global turn
    turn += 1
    turn = min(turn, turns-1)
    
def previous_turn():
    global turn
    turn -= 1
    turn = max(turn, 0)
    
# graphics    
def draw(board):
    windowSurfObj.fill(black)

    # draw background
    drawBackground(windowSurfObj)
    
    # draw border
    pygame.draw.rect(windowSurfObj, white, (borderWidth,borderWidth,res[0]-borderWidth*2,res[1]-(fontSize + bottomPad + borderWidth*2)), 1)

    draw_board(windowSurfObj, board)
            

    
    # debug status
    if debug:
        pass
    else:
        drawText(windowSurfObj, 'Lives: ' + str(player.getLives()), (borderWidth, res[1] - (fontSize)))
        
    # stats
    drawText(windowSurfObj, 'Score: ' + str(player.getPoints()), (res[0]*3/5 , res[1] - (fontSize)))
    drawText(windowSurfObj, 'Turn: ' + str(turn), (res[0]*4/5 , res[1] - (fontSize)))

def draw_board(wso, board):
    size = len(board)
    x = res[0]*1/10
    y = res[1]*1/5
    
    for row in range(size):
        for col in range(0,size*2,2):
            if (board[row][col] == '#'):
                draw_tile(wso, white, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
            if (board[row][col] == '@'):
                if board[row][col+1] == '1':
                    draw_tile(wso, red, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
                    drawText(wso, board[row][col+1], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH))
                if board[row][col+1] == '2':
                    draw_tile(wso, blue, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
                    drawText(wso, board[row][col+1], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH))
                if board[row][col+1] == '3':
                    draw_tile(wso, green, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
                    drawText(wso, board[row][col+1], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH))
                if board[row][col+1] == '4':
                    draw_tile(wso, yellow, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
                    drawText(wso, board[row][col+1], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH))
            if (board[row][col] == '$'):
                draw_tile(wso, brown, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
                drawText(wso, board[row][col+1], (x + col/2*BLOCK_WIDTH + 5, y + row*BLOCK_WIDTH + 2))
            if (board[row][col] == '['):
                draw_tile(wso, lightBlue, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
            if (board[row][col] == ' '):
                draw_tile(wso, black, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
            else:
                pass
                # draw_tile(wso, black, board[0], (x + col/2*BLOCK_WIDTH, y + row*BLOCK_WIDTH), BLOCK_WIDTH)
        
        drawText(wso, board[row], (res[0]*3/5, res[1]*1/5 + row*fontSize))
        
    
        
def draw_tile(wso, color, tile, coords, size):
    FILLED = 0
    pygame.draw.rect(wso, color, (coords[0], coords[1], size, size), FILLED)
    pygame.draw.rect(wso, gray(100), (coords[0], coords[1], size, size), 2)

    
    
def drawWaypoints(wso, waypoints):
    # draw legs
    for wp in waypoints:
        drawWaypoint(wso, wp)
            
def drawWaypoint(wso, wp):
    pygame.draw.circle(wso, wp.color, wp.getPos(), wp.radius, 0)

def drawBackground(wso):
    pygame.draw.circle(wso, gray(25), (res[0]/3 + 40, res[1]/3), 240)
    pygame.draw.circle(wso, gray(20), (res[0]*2/3, res[1]*2/3), 250)
    pygame.draw.circle(wso, gray(15), (res[0]*1/4, res[1]*4/5), 200)

def drawText(wso, string, coords):
    textSurfObj = fontObj.render(string, False, white)
    textRectObj = textSurfObj.get_rect()
    textRectObj.topleft = coords
    wso.blit(textSurfObj, textRectObj)

def updatePositions():
    
    if not paused:
        if any(pygame.event.get(pygame.USEREVENT)):
            next_turn()
        
def outOfBounds():
    player.takeLife()
    if not paused:
        togglePause()

def checkGame():
    if player.getLives() <= 0:
        resetGame()
    
def nextLevel():
    global game

    game.setLevel(game.getLevel() + 1)

    if not paused:
        togglePause()

def resetGame():
    global game, player
    
    game.setLevel(1)
    
    if not paused:
        togglePause()
    
    player.setPoints(startingPoints)
    player.setLives(startingLives)

def open_file(fn):
    global turns
    f = open(fn, 'r')
    if f == None:
        print 'error opening input file', fn
        f = None
    else:
        sep = re.compile('^\s*$')
        all_boards = []
        
        for x in f:
            if x[0] != '\n':
                all_boards.append(x.strip('\n'))
            else:
                all_boards.append('')
    turns = all_boards.count('')
    f.close()
    return all_boards
    
def extract_board(boards, n):
    board = []
    size = len(boards)/boards.count('') - 1
    for x in range(size):
        board.append(boards[n*(size + 1) + x])    
    return board
    
boards = open_file(vfn)
    
# main program loop
while True:

    # check status, lives, bricks, etc
    checkGame()
    
    # update positions
    updatePositions()
    
    b = extract_board(boards, turn)
    
    # draw
    draw(b)
    
    # input
    processInput()
    pollInputs()

    # update draw
    pygame.display.update()
    fpsClock.tick(fps)
