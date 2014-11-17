'''
Created on Oct 31, 2014

@author: scrhoads
'''
import unittest
from minimax import Vindinium, alphabeta_search


class Test(unittest.TestCase):


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
#         """
        myHeroName = initial['hero']['name']
        v1 = Vindinium(myHeroName, initial)
        
#         actionList = v1.actions(initial)
#         print actionList
        
        """resultState = v1.result(initial, actionList[0])
        
        print v1.utility(resultState, myHeroName)
        """
                                
        
        move = alphabeta_search(v1, d=1)
        print move


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGetClosestMineAtBeginning']
    unittest.main()