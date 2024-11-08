import sys
import pygame as pg
from pygame.locals import *

#Yawn Pygame Stuff
pg.init()
screenSize = (1200,800)
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


while(True):
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()

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
        print(zoomScale)
    if keys[pg.K_q] and zoomScale>0.2:
        zoomScale=zoomScale/1.04
        print(zoomScale)



    #Drawing World Map
    world.blit(worldMap, (0,0))

    #DRAW HERE WORLD ELEMENTS HERE-------------------------------------------

    pg.draw.rect(world,"red",(2120-1,1550-1,2,2))


    #------------------------------------------------------------------------

    #Cropping (to save on ram), Zooming, and Displaying World on "screen"
    worldCropped=pg.Surface((screenSize[0]/zoomScale,screenSize[1]/zoomScale))
    worldCropped.blit(world,(0,0),((cameraCoords[0])-screenSize[0]/(2*zoomScale),(cameraCoords[1])-screenSize[1]/(2*zoomScale),screenSize[0]/zoomScale,screenSize[1]/zoomScale))
    worldCroppedScaled = pg.transform.scale(worldCropped,screenSize)#can use smoothscale under certain zoomScale value
    screen.blit(worldCroppedScaled, (0,0))

    #DRAW HERE UI ELEMENTS HERE----------------------------------------------

    pg.draw.rect(screen,"cyan",(0,screenSize[1]-30,screenSize[0],30))


    #------------------------------------------------------------------------




    pg.display.flip()
    fpsClock.tick(60)
