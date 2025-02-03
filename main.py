from game import *
import pygame as pg
import sys
from threading import Thread
from server import activate_server
from pygame.locals import *
from nodes import *
from game import GameState
from game import *

#========================================================================================================================================
#   To do list:
#
#       - invaders attacks -> Armen
#       - player abilities -> Armen
#       - invader resources
#           * resource generation over time should be scaled per player count
#       - add UI + Minimap
#
#========================================================================================================================================



#start up local server
game_server = Thread(target=activate_server)
game_server.start()



Begin_Invasion()