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
# test
#
#
#
#
#
#
#========================================================================================================================================



#start up local server
game_server = Thread(target=activate_server)
game_server.start()



Begin_Invasion()
