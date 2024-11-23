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
            elif event.type == MOUSEWHEEL:
                player.mouseWheel = event.y

                

    player.process_user_input()
    player.updatePlayerCamera()

    player.eAbilityTick()#must happen before updatePOS()
    

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

    #draw all nodes and network edges
    # for currNode in list(pathfindingNetwork.keys()):
    #         pg.draw.circle(screen,"grey", worldToScreenCoords(currNode), 4)
    #         for targetNode in pathfindingNetwork.get(currNode):
    #             pg.draw.aaline(screen,"grey", worldToScreenCoords(currNode), worldToScreenCoords(targetNode))
    
    
    #Shows Nodes in LOS of player
    # for node in list(pathfindingNetwork.keys()):
    #         isInLos, _ = lineOfSight(player.position,node)
    #         if isInLos:
    #             pg.draw.aaline(screen,"grey", worldToScreenCoords(player.position), worldToScreenCoords(node))
    
    #Shows Nodes in LOS of player's final waypoint
    # if player.path != []:
    #     for node in list(pathfindingNetwork.keys()):
    #             isInLos, _ = lineOfSight(player.path[-1],node)
    #             if isInLos:
    #                 pg.draw.aaline(screen,"grey", worldToScreenCoords(player.path[-1]), worldToScreenCoords(node))
    #------------------------------------------------------------------------

    #standard game loop
    pg.display.flip()
    clock.tick(60)
