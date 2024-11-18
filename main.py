from game import *
import pygame as pg
import numpy as np
import sys
from threading import Thread
from server import activate_server
from pygame.locals import *
import time

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

#player declaration
player = Player(2000, 1600)

#student army declaration
studentArmy = []



def screenToWorldCoords(screenCoord):
    return (cameraCoords[0]-(screenSize[0]/2-screenCoord[0])/zoomScale,cameraCoords[1]-(screenSize[1]/2-screenCoord[1])/zoomScale)

def worldToScreenCoords(worldCoord):
    return ((worldCoord[0]-cameraCoords[0])*zoomScale+screenSize[0]/2,(worldCoord[1]-cameraCoords[1])*zoomScale+screenSize[1]/2)

def read_student_input():
    with open('student_input.txt', 'r+') as f:
        for line in f:
            print(line)
        f.seek(0)
        f.truncate()

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
    
    if Mouse_R:
        isInLosForPlayerMovement, losCollForPlayerMovement = lineOfSight(player.position,screenToWorldCoords(pg.mouse.get_pos()))
        if isInLosForPlayerMovement:
            player.process_user_input(screenToWorldCoords(pg.mouse.get_pos()))
        else:
            player.process_user_input(losCollForPlayerMovement)
    


    #Drawing World Map
    world.blit(worldMap, (0,0))

    #DRAW HERE WORLD ELEMENTS HERE-------------------------------------------
    player.draw(world)


    #player update
    player.update()
    
    #pg.draw.rect(world,"red",(2120-1,1550-1,2,2))

    temporaryLosBool, losContactCoord = lineOfSight(cameraCoords,screenToWorldCoords(Mouse_Pos))

            
    #------------------------------------------------------------------------

    #Cropping (to save on ram), Zooming, and Displaying World on "screen"
    worldCropped=pg.Surface((screenSize[0]/zoomScale,screenSize[1]/zoomScale))
    worldCropped.blit(world,(0,0),((cameraCoords[0])-screenSize[0]/(2*zoomScale),(cameraCoords[1])-screenSize[1]/(2*zoomScale),screenSize[0]/zoomScale,screenSize[1]/zoomScale))
    worldCroppedScaled = pg.transform.scale(worldCropped,screenSize)#can use smoothscale under certain zoomScale value
    screen.blit(worldCroppedScaled, (0,0))

    #DRAW HERE UI ELEMENTS HERE----------------------------------------------

    #pg.draw.rect(screen,"cyan",(0,screenSize[1]-30,screenSize[0],30))
    if debugMode:
        pg.draw.rect(screen,"green",(screenSize[0]/2-5,screenSize[1]/2-5,10,10))
        pg.draw.line(screen,"purple",(screenSize[0]/2,screenSize[1]/2),(Mouse_Pos))

    #------------------------------------------------------------------------

    #standard game loop
    pg.display.flip()
    clock.tick(60)
