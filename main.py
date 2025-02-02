from game import *
import pygame as pg
import sys
from threading import Thread
from server import activate_server
from pygame.locals import *
from nodes import *
from game import controlPointLocations
from game import *

#========================================================================================================================================
#   To do list:
#
#       - invaders attacks -> Armen
#       - player abilities -> Armen
#       - invader resources
#           * add resource generation over time (should be scaled per player count)
#       - add UI + Minimap
#
#========================================================================================================================================

#Debug mode
debugMode = False

#start up local server
game_server = Thread(target=activate_server)
game_server.start()

while True:
    
    if GameState == 0:
        MainMenu()
        
    elif GameState == 1:
        playMainGame()

    elif GameState == 2:
        GameEndScreen()
        

    #standard game loop
    pg.display.flip()
    clock.tick(60)
