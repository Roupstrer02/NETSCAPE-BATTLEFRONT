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

#init declarations
screenSize = (1200,800)
pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode(screenSize)
pg.display.set_caption('NETSCAPE: BATTLEFRONT')
fpsClock = pg.time.Clock()


#Loading Map Image, some Surface inits
worldMap = pg.image.load("Map - Iso.png").convert()
worldCroppedScaled=pg.Surface(screenSize)
world=pg.Surface((5080,2660))#size of the PNG must never change


#Params
startingCameraWorldCoords = [2540,1340]#<--Change Starting Camera Coords Here
startingZoomScale = 1#<--------------------Change Starting Zoom Scale Here

cameraCoords = startingCameraWorldCoords
zoomScale = startingZoomScale

#student army declaration
studentArmy = []


def screenToWorldCoords(screenCoord):
    return (cameraCoords[0]-(screenSize[0]/2-screenCoord[0])/zoomScale,cameraCoords[1]-(screenSize[1]/2-screenCoord[1])/zoomScale)

def worldToScreenCoords(worldCoord):
    return ((worldCoord[0]-cameraCoords[0])*zoomScale+screenSize[0]/2,(worldCoord[1]-cameraCoords[1])*zoomScale+screenSize[1]/2)


while True:
    #Updates <-could be a better name
    pg.event.pump()
    read_student_input()

    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()




    
    Mouse_Pos = pg.mouse.get_pos()
    Mouse_L, Mouse_M, Mouse_R = pg.mouse.get_pressed()
    keys=pg.key.get_pressed()
    if keys[pg.K_a]:
        cameraCoords[0]-=10/zoomScale
    if keys[pg.K_d]:
        cameraCoords[0]+=10/zoomScale
    if keys[pg.K_w]:
        cameraCoords[1]-=10/zoomScale
    if keys[pg.K_s]:
        cameraCoords[1]+=10/zoomScale

    if keys[pg.K_e] and zoomScale<14:
        zoomScale=zoomScale*1.04 
    if keys[pg.K_q] and zoomScale>0.2:
        zoomScale=zoomScale/1.04
    

    if keys[pg.K_SPACE]:
        while(keys[pg.K_SPACE]):
            pg.event.pump()
            keys=pg.key.get_pressed()
        pass

    

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
    worldCropped=pg.Surface((screenSize[0]/zoomScale,screenSize[1]/zoomScale))
    worldCropped.blit(world,(0,0),((cameraCoords[0])-screenSize[0]/(2*zoomScale),(cameraCoords[1])-screenSize[1]/(2*zoomScale),screenSize[0]/zoomScale,screenSize[1]/zoomScale))
    worldCroppedScaled = pg.transform.scale(worldCropped,screenSize)#can use smoothscale under certain zoomScale value
    screen.blit(worldCroppedScaled, (0,0))

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
