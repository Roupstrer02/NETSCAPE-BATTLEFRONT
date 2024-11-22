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
    player.draw(world)
    for invader in invadersOnMap:
        invader.update()
        invader.draw(world)

    #player update
    player.update()
    
    #pg.draw.rect(world,"red",(2120-1,1550-1,2,2))

    

            

    #------------------------------------------------------------------------

    #Cropping (to save on ram), Zooming, and Displaying World on "screen"
    cropWorldView()

    #DRAW HERE UI ELEMENTS HERE----------------------------------------------

    #pg.draw.rect(screen,"cyan",(0,screenSize[1]-30,screenSize[0],30))
    
    # for currNode in list(pathfindingNetwork.keys()):
    #     pg.draw.circle(screen, (200, 200, 200), worldToScreenCoords(currNode), 6)
    #     for targetNode in pathfindingNetwork[currNode]:
    #         pg.draw.aaline(screen, (200, 200, 200),worldToScreenCoords(currNode),worldToScreenCoords(targetNode))


    # path = generatePath(cameraCoords,screenToWorldCoords(Mouse_Pos))
    
    # if path != None:
    #     waypoints = path[0]
    #     pg.draw.circle(screen,"red", worldToScreenCoords(cameraCoords), 6)
    #     pg.draw.aaline(screen,"red", worldToScreenCoords(cameraCoords), worldToScreenCoords(waypoints[-1]))
        
    #     for node in waypoints:
    #         pg.draw.circle(screen,"red", worldToScreenCoords(node), 6)
    #     for i in range(len(waypoints)-1):
    #         pg.draw.aaline(screen,"red", worldToScreenCoords(waypoints[i]), worldToScreenCoords(waypoints[i+1]))


    #------------------------------------------------------------------------

    #standard game loop
    pg.display.flip()
    clock.tick(60)
