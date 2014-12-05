'''
Created on Oct 31, 2014

@author: scrhoads
'''
import unittest
from minimax import Vindinium, multiplayer_minimax_search, getZeroBasedPlayerIdForThisTurn
from time import time


class Test(unittest.TestCase):
    
    
    def testPlayerTurnCalcTurn0(self):
        initial = {u'viewUrl': u'http://vindinium.org/cl7m3tme', 
                   u'game': 
                        {
                         u'turn': 0,
                         u'heroes': [
                                     {u'life': 100, u'numMoves': 0, u'elo': 1258, u'gold': 10, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 5, u'x': 15}, u'spawnPos': {u'y': 5, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 2}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 12, u'x': 15}, u'spawnPos': {u'y': 12, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 3}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 12, u'x': 2}, u'spawnPos': {u'y': 12, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 4}], 
                        },
                    u'hero': {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                   } 
        myHeroName = initial['game']['heroes'][0]['name']
       
        v1 = Vindinium(myHeroName, initial)
        
        zeroBasedPlayerId = getZeroBasedPlayerIdForThisTurn(initial)
       
        expectedId = 0
       
        self.assertEqual(expectedId, zeroBasedPlayerId, str(expectedId) + " is expected, but received: " + str(zeroBasedPlayerId))
        
    def testPlayerTurnCalcTurns(self):
        initial = {u'viewUrl': u'http://vindinium.org/cl7m3tme', 
                   u'game': 
                        {
                         u'turn': 1,
                         u'heroes': [
                                     {u'life': 100, u'numMoves': 0, u'elo': 1258, u'gold': 10, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 5, u'x': 15}, u'spawnPos': {u'y': 5, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 2}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 12, u'x': 15}, u'spawnPos': {u'y': 12, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 3}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 12, u'x': 2}, u'spawnPos': {u'y': 12, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 4}], 
                        },
                    u'hero': {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                   } 
        myHeroName = initial['game']['heroes'][0]['name']
       
        v1 = Vindinium(myHeroName, initial)
        
        zeroBasedPlayerId = getZeroBasedPlayerIdForThisTurn(initial)
       
        expectedId = 1
       
        self.assertEqual(expectedId, zeroBasedPlayerId, str(expectedId) + " is expected, but received: " + str(zeroBasedPlayerId))
        
        initial['game']['turn'] = 2
        
        zeroBasedPlayerId = getZeroBasedPlayerIdForThisTurn(initial)
        self.assertEqual(2, zeroBasedPlayerId, str(2) + " is expected, but received: " + str(zeroBasedPlayerId))

        initial['game']['turn'] = 3
        
        zeroBasedPlayerId = getZeroBasedPlayerIdForThisTurn(initial)
        self.assertEqual(3, zeroBasedPlayerId, str(3) + " is expected, but received: " + str(zeroBasedPlayerId))
        
        
        initial['game']['turn'] = 4
        
        zeroBasedPlayerId = getZeroBasedPlayerIdForThisTurn(initial)
        self.assertEqual(0, zeroBasedPlayerId, str(0) + " is expected, but received: " + str(zeroBasedPlayerId))
        
        
        initial['game']['turn'] = 5
        
        zeroBasedPlayerId = getZeroBasedPlayerIdForThisTurn(initial)
        self.assertEqual(1, zeroBasedPlayerId, str(1) + " is expected, but received: " + str(zeroBasedPlayerId))
    
    def testUtilityVectorGenNoNumMoves(self):
        initial = {u'viewUrl': u'http://vindinium.org/cl7m3tme', 
                   u'game': 
                        {
                         u'heroes': [
                                     {u'life': 100, u'numMoves': 0, u'elo': 1258, u'gold': 10, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 5, u'x': 15}, u'spawnPos': {u'y': 5, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 2}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 12, u'x': 15}, u'spawnPos': {u'y': 12, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 3}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 12, u'x': 2}, u'spawnPos': {u'y': 12, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 4}], 
                        },
                    u'hero': {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                   }
        myHeroName = initial['game']['heroes'][0]['name']

        v1 = Vindinium(myHeroName, initial)
        utilVector = v1.utility(initial)
        
        playerOUtility = utilVector[0]
        
        expectedVal = 4
        self.assertEqual(expectedVal, playerOUtility, "expected utility of " + str(expectedVal) + " (10-6) but received: " + str(playerOUtility))
        
    def testUtilityVectorGen10MovesPlayer0(self):
        initial = {u'viewUrl': u'http://vindinium.org/cl7m3tme', 
                   u'game': 
                        {
                         u'heroes': [
                                     {u'life': 100, u'numMoves': 4, u'elo': 1258, u'gold': 10, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 5, u'x': 15}, u'spawnPos': {u'y': 5, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 2}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 12, u'x': 15}, u'spawnPos': {u'y': 12, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 3}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 2, u'pos': {u'y': 12, u'x': 2}, u'spawnPos': {u'y': 12, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 4}], 
                        },
                    u'hero': {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                   }
        myHeroName = initial['game']['heroes'][0]['name']

        v1 = Vindinium(myHeroName, initial)
        utilVector = v1.utility(initial)
        
        playerOUtility = float(utilVector[0])
        
        expectedVal = 2.61370563888
        self.assertAlmostEqual(expectedVal, playerOUtility, 11, "expected utility of " + str(expectedVal) + " (10-6) but received: " + str(playerOUtility))


    def testGetClosestMineAtBeginning(self):
        """
        initial = {u'viewUrl': u'http://vindinium.org/cl7m3tme', 
                   u'game': 
                        {u'turn': 0, 
                         u'finished': False, 
                         u'board': 
                            {u'tiles': 
                                u'####################################################$-$-##########################@1[]##    ##[]@4####################  ##        ##  ################$-    ####    ####    $-################                ##################                    ##############    ##  ########  ##    ############  $-##  ########  ##$-  ############  $-##  ########  ##$-  ############    ##  ########  ##    ##############                    ##################                ################$-    ####    ####    $-################  ##        ##  ####################@2[]##    ##[]@3##########################$-$-####################################################', 
                                u'size': 18}, 
                         u'heroes': [
                                     {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                                     {u'life': 100, u'name': u'random', u'gold': 0, u'pos': {u'y': 5, u'x': 15}, u'spawnPos': {u'y': 5, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 2}, 
                                     {u'life': 100, u'name': u'random', u'gold': 0, u'pos': {u'y': 12, u'x': 15}, u'spawnPos': {u'y': 12, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 3}, 
                                     {u'life': 100, u'name': u'random', u'gold': 0, u'pos': {u'y': 12, u'x': 2}, u'spawnPos': {u'y': 12, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 4}], 
                         u'id': u'cl7m3tme', 
                         u'maxTurns': 800}, 
                         u'hero': {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                         u'token': u'66fv', 
                         u'playUrl': u'http://vindinium.org/api/cl7m3tme/66fv/play'
                        }
        """
#         """
        initial = {u'viewUrl': u'http://vindinium.org/cl7m3tme', 
                   u'game': 
                        {u'turn': 0, 
                         u'finished': False, 
                         u'board': 
                            {u'tiles': 
                                u'####################################################$-##########################@1[]##    ##[]@4####################  ##        ##  ################$-    ####    ####    ##################                ##################                    ##############    ##  ########  ##    ############  ####  ########  ####  ############  ####  ########  ####  ############    ##  ########  ##    ##############                    ##################                ##################    ####    ####    ##################  ##        ##  ####################@2[]##    ##[]@3##################################################################################', 
                                u'size': 18}, 
                         u'heroes': [
                                     {u'life': 100, u'numMoves': 0, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 0, u'pos': {u'y': 5, u'x': 15}, u'spawnPos': {u'y': 5, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 2}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 0, u'pos': {u'y': 12, u'x': 15}, u'spawnPos': {u'y': 12, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 3}, 
                                     {u'life': 100, u'numMoves': 0, u'name': u'random', u'gold': 0, u'pos': {u'y': 12, u'x': 2}, u'spawnPos': {u'y': 12, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 4}], 
                         u'id': u'cl7m3tme', 
                         u'maxTurns': 800}, 
                         u'hero': {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                         u'token': u'66fv', 
                         u'playUrl': u'http://vindinium.org/api/cl7m3tme/66fv/play'
                        }
#         """
        myHeroName = initial['hero']['name']
        v1 = Vindinium(myHeroName, initial)
        move = multiplayer_minimax_search(v1, d=0)
#         print move
        

    def testTimeBigGameBoard(self):
        initial = {u'viewUrl': u'http://vindinium.org/cl7m3tme', 
                   u'game': 
                        {u'turn': 0, 
                         u'finished': False, 
                         u'board': 
                            {u'tiles': 
                                u'    $-                                            $-        @1  $-##                                ##$-                        ##      ##    ##      ##          @4                      ##  ##        ##  ##                            ##  $-  $-  $-        $-  $-  $-  ##          $-      ##    $-                        $-    ##      $-  $-####    ####        $-    $-        ####    ####$-                        ##        ##                                            ##        ##                      ##    ##  ##                                ##  ##    ##  ##      []        ##  ##$-$-##  ##        []      ##            ##    $-      $-    $-      $-    ##                                  ##    ##                                                                                                                                                                ##    ##                                  ##    $-      $-    $-      $-    ##            ##      []        ##  ##$-$-##  ##        []      ##  ##    ##  ##                                ##  ##    ##                      ##        ##                                            ##        ##                        $-####    ####        $-    $-        ####    ####$-  $-      ##    $-                        $-    ##      $-          ##  $-  $-  $-        $-  $-  $-  ##                            ##  ##        ##  ##                      @2          ##      ##    ##      ##          @3            $-##                                ##$-            $-                                            $-    ',
                                u'size': 28}, 
                         u'heroes': [
                                     {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                                     {u'life': 100, u'name': u'random', u'gold': 0, u'pos': {u'y': 5, u'x': 15}, u'spawnPos': {u'y': 5, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 2}, 
                                     {u'life': 100, u'name': u'random', u'gold': 0, u'pos': {u'y': 12, u'x': 15}, u'spawnPos': {u'y': 12, u'x': 15}, u'crashed': False, u'mineCount': 0, u'id': 3}, 
                                     {u'life': 100, u'name': u'random', u'gold': 0, u'pos': {u'y': 12, u'x': 2}, u'spawnPos': {u'y': 12, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 4}], 
                         u'id': u'cl7m3tme', 
                         u'maxTurns': 800}, 
                         u'hero': {u'life': 100, u'elo': 1258, u'gold': 0, u'userId': u'slzu4yoo', u'pos': {u'y': 5, u'x': 2}, u'spawnPos': {u'y': 5, u'x': 2}, u'crashed': False, u'mineCount': 0, u'id': 1, u'name': u'sirrambot1'}, 
                         u'token': u'66fv', 
                         u'playUrl': u'http://vindinium.org/api/cl7m3tme/66fv/play'
                        }
        myHeroName = initial['hero']['name']
        t0 = time()
        v1 = Vindinium(myHeroName, initial)
        move = multiplayer_minimax_search(v1, d=0)
        tdiff = time() - t0
        print "took : " + str(tdiff) + " sec"
        print "timeBigGameBoard\n"
        print "tiles: " + str(initial['game']['board']['size'])

        print move
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetClosestMineAtBeginning']
    unittest.main()