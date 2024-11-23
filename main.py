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
#       - Continue standard game development
#
#========================================================================================================================================

#Debug mode
debugMode = False

#start up local server
game_server = Thread(target=activate_server)
game_server.start()




while True:
    #Updates <-could be a better name
    
    read_student_input()

    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()

    player.process_user_input()
    
    player.updatePlayerCamera()

    

    #Drawing World Map
    world.blit(worldMap, (0,0))

    #DRAW HERE WORLD ELEMENTS HERE-------------------------------------------
    drawControlPoints()
    
    player.drawOnWorld()
    
    for invader in invadersOnMap:
        invader.update()
        invader.draw(world)

    #player update
    player.pathfind()
    player.updatePos()
    
    #pg.draw.rect(world,"red",(2120-1,1550-1,2,2))

    

            

    #------------------------------------------------------------------------

    #Cropping (to save on ram), Zooming, and Displaying World on "screen"
    cropWorldView()

    #DRAW HERE UI ELEMENTS HERE----------------------------------------------
    player.drawOnWorld()
    
    
    #TEMP: MOVE TO DEBUG MODE
    if player.path != []:
            waypoints = player.path
            pg.draw.aaline(screen,"red", worldToScreenCoords(player.position), worldToScreenCoords(waypoints[0]))

            for node in waypoints:
                pg.draw.circle(screen,"red", worldToScreenCoords(node), 6)
            for i in range(len(waypoints)-1):
                pg.draw.aaline(screen,"red", worldToScreenCoords(waypoints[i]), worldToScreenCoords(waypoints[i+1]))


    #------------------------------------------------------------------------

    #standard game loop
    pg.display.flip()
    clock.tick(60)
