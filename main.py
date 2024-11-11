#from game import * <-phased out for now
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

#student army declaration
studentArmy = []


#List of all walls, and pre calculated values
allWallEdgesList=[[(2820, 1020), (2740, 980), (2960, 1090), (2800, 1090), (2840, 1110), (2860, 1100), (2880, 1130), (2860, 1120), (2840, 1130), (3120, 1150), (3080, 1130), (2960, 1190), (3120, 1230), (3080, 1210), (2920, 1070), (2900, 1060), (2880, 1070), (2820, 1040), (2840, 1030), (2820, 1020), (2780, 1040), (2880, 1090), (2980, 1160), (2900, 1120), (2980, 1080), (3060, 1120), (3120, 1230), (3160, 1210), (3080, 1170), (3120, 1150), (3140, 1160), (3120, 1170), (3200, 1210), (3140, 1240), (2600, 1230), (2720, 1170), (2680, 1150), (2700, 1140), (2660, 1120), (2680, 1110), (2740, 1140), (2720, 1150), (2780, 1180), (2880, 1130), (2940, 1160), (2840, 1210), (2920, 1250), (2940, 1240), (2980, 1260), (2940, 1280), (2920, 1270), (2900, 1280), (2880, 1270), (2740, 1340), (2720, 1330), (2840, 1270), (2780, 1240), (2760, 1250), (2720, 1230), (2700, 1240), (2660, 1220), (2620, 1240), (2460, 1020), (2580, 960), (2640, 990), (2540, 1040), (2640, 1090), (2620, 1100), (2520, 1110), (2540, 1100), (2600, 1130), (2580, 1140), (2620, 1160), (2520, 1210), (2420, 1160), (2440, 1150), (2420, 1140), (2440, 1130), (2420, 1120), (2440, 1110), (2380, 1080), (2400, 1070), (2520, 1130), (2540, 1120), (2040, 1550), (2080, 1530), (2100, 1540), (2340, 1420), (2320, 1410), (2340, 1400), (2420, 1440), (2400, 1450), (2380, 1440), (2360, 1450), (2340, 1440), (2120, 1550), (2200, 1590), (2160, 1610), (2340, 1240), (2360, 1230), (2340, 1220), (2360, 1210), (2340, 1200), (2360, 1190), (2460, 1240), (2400, 1270), (2360, 1350), (2400, 1370), (2460, 1340), (2440, 1330), (2600, 1250), (2580, 1240), (2640, 1270), (2660, 1260), (2700, 1280), (2660, 1300), (2640, 1290), (2660, 1280), (2540, 1340), (2580, 1320), (2600, 1330), (2580, 1340), (2600, 1350), (2580, 1360), (2440, 1390), (2480, 1370), (2520, 1390), (2500, 1400), (2540, 1420), (2700, 1340), (2720, 1350), (2540, 1440), (2660, 1500), (2820, 1420), (2760, 1390), (2600, 1470), (2420, 1460), (2440, 1450), (2540, 1500), (2520, 1510), (2400, 1570), (2440, 1550), (2420, 1540), (2440, 1530), (2420, 1520), (2440, 1510), (2480, 1530), (2460, 1540), (2480, 1550), (2420, 1580), (2220, 1540), (2260, 1520), (2320, 1550), (2280, 1570), (2100, 1400), (2060, 1380), (2100, 1360), (2120, 1370), (2140, 1360), (2180, 1380), (2140, 1400), (2120, 1390), (1980, 1440), (2000, 1430), (1980, 1420), (2020, 1400), (2060, 1420), (2040, 1430), (2060, 1440), (2020, 1460), (1800, 1630), (1820, 1620), (1800, 1610), (1820, 1600), (1800, 1590), (1960, 1510), (1980, 1520), (2020, 1500), (1900, 1440), (1920, 1430), (1900, 1420), (1920, 1410), (1900, 1400), (1940, 1380), (1920, 1370), (2000, 1330), (2020, 1340), (2060, 1320), (2080, 1330), (2100, 1320), (2120, 1330), (2140, 1320), (2260, 1380), (2280, 1370), (2240, 1350), (2340, 1300), (2240, 1250), (2260, 1240), (2240, 1230), (2260, 1220), (2240, 1210), (2260, 1200), (2160, 1150), (2180, 1140), (2160, 1130), (2180, 1120), (2160, 1110), (2260, 1060), (2280, 1070), (2300, 1060), (2320, 1070), (2340, 1060), (2360, 1070), (2400, 1050), (2500, 1100), (2520, 1090), (2340, 1000), (2380, 980), (2420, 1000), (2560, 930), (2660, 980), (2720, 950), (2840, 1010), (2880, 990), (3280, 1190), (3120, 1270), (3100, 1260), (3120, 1250), (3080, 1230), (3060, 1240), (3080, 1250), (3060, 1260), (3100, 1280), (3040, 1310), (3020, 1300), (2980, 1320), (2960, 1310), (2940, 1320), (2920, 1310), (2820, 1360), (2880, 1390), (2900, 1380), (3040, 1450), (3020, 1460), (3040, 1470), (3020, 1480), (3040, 1490), (2860, 1580), (2840, 1570), (2800, 1590), (2780, 1580), (2740, 1600), (2560, 1510), (2520, 1530), (2540, 1540), (2500, 1560), (2520, 1570), (2340, 1660), (2260, 1620), (2060, 1720), (2040, 1710), (2020, 1720), (2000, 1710), (1980, 1720)], 
                  [(2740, 980), (2600, 1050), (2920, 1070), (2840, 1110), (2860, 1100), (2900, 1120), (2860, 1120), (2840, 1130), (2780, 1100), (3080, 1130), (2960, 1190), (2920, 1170), (3080, 1210), (3040, 1230), (2900, 1060), (2880, 1070), (2820, 1040), (2840, 1030), (2820, 1020), (2780, 1040), (2880, 1090), (2920, 1070), (2900, 1120), (2980, 1080), (3060, 1120), (2980, 1160), (3160, 1210), (3080, 1170), (3120, 1150), (3140, 1160), (3120, 1170), (3200, 1210), (3140, 1240), (3120, 1230), (2720, 1170), (2680, 1150), (2700, 1140), (2660, 1120), (2680, 1110), (2740, 1140), (2720, 1150), (2780, 1180), (2880, 1130), (2940, 1160), (2840, 1210), (2920, 1250), (2940, 1240), (2980, 1260), (2940, 1280), (2920, 1270), (2900, 1280), (2880, 1270), (2740, 1340), (2720, 1330), (2840, 1270), (2780, 1240), (2760, 1250), (2720, 1230), (2700, 1240), (2660, 1220), (2620, 1240), (2600, 1230), (2580, 960), (2640, 990), (2540, 1040), (2640, 1090), (2620, 1100), (2460, 1020), (2540, 1100), (2600, 1130), (2580, 1140), (2620, 1160), (2520, 1210), (2420, 1160), (2440, 1150), (2420, 1140), (2440, 1130), (2420, 1120), (2440, 1110), (2380, 1080), (2400, 1070), (2520, 1130), (2540, 1120), (2520, 1110), (2080, 1530), (2100, 1540), (2340, 1420), (2320, 1410), (2340, 1400), (2420, 1440), (2400, 1450), (2380, 1440), (2360, 1450), (2340, 1440), (2120, 1550), (2200, 1590), (2160, 1610), (2040, 1550), (2360, 1230), (2340, 1220), (2360, 1210), (2340, 1200), (2360, 1190), (2460, 1240), (2400, 1270), (2340, 1240), (2400, 1370), (2460, 1340), (2440, 1330), (2600, 1250), (2580, 1240), (2360, 1350), (2660, 1260), (2700, 1280), (2660, 1300), (2640, 1290), (2660, 1280), (2640, 1270), (2580, 1320), (2600, 1330), (2580, 1340), (2600, 1350), (2580, 1360), (2540, 1340), (2480, 1370), (2520, 1390), (2500, 1400), (2540, 1420), (2700, 1340), (2720, 1350), (2540, 1440), (2440, 1390), (2820, 1420), (2760, 1390), (2600, 1470), (2660, 1500), (2440, 1450), (2540, 1500), (2520, 1510), (2420, 1460), (2440, 1550), (2420, 1540), (2440, 1530), (2420, 1520), (2440, 1510), (2480, 1530), (2460, 1540), (2480, 1550), (2420, 1580), (2400, 1570), (2260, 1520), (2320, 1550), (2280, 1570), (2220, 1540), (2060, 1380), (2100, 1360), (2120, 1370), (2140, 1360), (2180, 1380), (2140, 1400), (2120, 1390), (2100, 1400), (2000, 1430), (1980, 1420), (2020, 1400), (2060, 1420), (2040, 1430), (2060, 1440), (2020, 1460), (1980, 1440), (1820, 1620), (1800, 1610), (1820, 1600), (1800, 1590), (1960, 1510), (1980, 1520), (2020, 1500), (1900, 1440), (1920, 1430), (1900, 1420), (1920, 1410), (1900, 1400), (1940, 1380), (1920, 1370), (2000, 1330), (2020, 1340), (2060, 1320), (2080, 1330), (2100, 1320), (2120, 1330), (2140, 1320), (2260, 1380), (2280, 1370), (2240, 1350), (2340, 1300), (2240, 1250), (2260, 1240), (2240, 1230), (2260, 1220), (2240, 1210), (2260, 1200), (2160, 1150), (2180, 1140), (2160, 1130), (2180, 1120), (2160, 1110), (2260, 1060), (2280, 1070), (2300, 1060), (2320, 1070), (2340, 1060), (2360, 1070), (2400, 1050), (2500, 1100), (2520, 1090), (2340, 1000), (2380, 980), (2420, 1000), (2560, 930), (2660, 980), (2720, 950), (2840, 1010), (2880, 990), (3280, 1190), (3120, 1270), (3100, 1260), (3120, 1250), (3080, 1230), (3060, 1240), (3080, 1250), (3060, 1260), (3100, 1280), (3040, 1310), (3020, 1300), (2980, 1320), (2960, 1310), (2940, 1320), (2920, 1310), (2820, 1360), (2880, 1390), (2900, 1380), (3040, 1450), (3020, 1460), (3040, 1470), (3020, 1480), (3040, 1490), (2860, 1580), (2840, 1570), (2800, 1590), (2780, 1580), (2740, 1600), (2560, 1510), (2520, 1530), (2540, 1540), (2500, 1560), (2520, 1570), (2340, 1660), (2260, 1620), (2060, 1720), (2040, 1710), (2020, 1720), (2000, 1710), (1980, 1720), (1800, 1630)]]

allWallEdgesMatrix = np.array(allWallEdgesList)
allWallEdgeMatrixMathPreCalcA = np.subtract(allWallEdgesMatrix[1,:,0],allWallEdgesMatrix[0,:,0])
allWallEdgeMatrixMathPreCalcB = np.subtract(np.multiply(allWallEdgesMatrix[0,:,1],allWallEdgesMatrix[1,:,0]),np.multiply(allWallEdgesMatrix[1,:,1],allWallEdgesMatrix[0,:,0]))
allWallEdgeMatrixMathPreCalcC = np.subtract(allWallEdgesMatrix[1,:,1],allWallEdgesMatrix[0,:,1])

# WARNING!!!!!!   Line indicated below can not detect wall when target and origin are horizontal
#                    v v both are (x,y)
def lineOfSight(origin,target):
    
    
    if (target[0]==origin[0]):
        target=(target[0]+0.001,target[1])
    
    deltaXIntermediate = target[0]-origin[0]
    #vvThis line is at fault
    xThresh = np.divide(np.subtract(np.multiply(deltaXIntermediate,allWallEdgeMatrixMathPreCalcB),np.multiply(allWallEdgeMatrixMathPreCalcA,(origin[1]*target[0]-origin[0]*target[1]))),np.subtract(   np.multiply(allWallEdgeMatrixMathPreCalcA,(target[1]-origin[1]))    ,    np.multiply(allWallEdgeMatrixMathPreCalcC,deltaXIntermediate)     ))
    isNotInLineOfSight = 0 != np.add(np.multiply(np.full((len(xThresh)),origin[0])<=xThresh, np.full((len(xThresh)),target[0])>=xThresh), np.multiply(np.full((len(xThresh)),origin[0])>=xThresh, np.full((len(xThresh)),target[0])<=xThresh))                                   &                                np.add(          np.multiply(allWallEdgesMatrix[0,:,0]<xThresh , allWallEdgesMatrix[1,:,0]>xThresh)      ,      np.multiply(allWallEdgesMatrix[0,:,0]>xThresh, allWallEdgesMatrix[1,:,0]<xThresh)         )    
    
    isAnyNotInLineOfSignt = isNotInLineOfSight.any()
    contactCoord=(0,0)

    isAnyInLineOfSignt = not(isAnyNotInLineOfSignt)

    if isAnyNotInLineOfSignt:
        distToAllActiveXThresh=np.divide(1,np.add(1,np.multiply(np.multiply(np.subtract(xThresh,target[0]),np.subtract(xThresh,target[0])),isNotInLineOfSight)))
        indexOfHitWall = np.argmin(distToAllActiveXThresh)
        yOfxThresh = ((target[1]-origin[1])/(target[0]-origin[0])) * (xThresh[indexOfHitWall]-origin[0])+origin[1]
        contactCoord = (xThresh[indexOfHitWall],yOfxThresh)

        #vv Bool of if in LOS        v Coords if in LOS
    return isAnyInLineOfSignt , contactCoord #, indexOfHitWall 






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

#temp
listOfPoints=[(0,0)]

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
    
    if Mouse_L:
        pg.event.pump()
        Mouse_L, Mouse_M, Mouse_R = pg.mouse.get_pressed()
        while(Mouse_L):
            pg.event.pump()
            Mouse_L, Mouse_M, Mouse_R = pg.mouse.get_pressed()
        Mouse_Pos_World = screenToWorldCoords(Mouse_Pos)
        roundedMouse_Pos_World = (round(Mouse_Pos_World[0]/20)*20,round(Mouse_Pos_World[1]/10)*10)
        if not(roundedMouse_Pos_World in listOfPoints):
            listOfPoints.append((round(Mouse_Pos_World[0]/20)*20,round(Mouse_Pos_World[1]/10)*10))
    
    if Mouse_R:
        pg.event.pump()
        Mouse_L, Mouse_M, Mouse_R = pg.mouse.get_pressed()
        while(Mouse_R):
            pg.event.pump()
            Mouse_L, Mouse_M, Mouse_R = pg.mouse.get_pressed()
        print(listOfPoints)
    
    
    #Drawing World Map
    world.blit(worldMap, (0,0))

    #DRAW HERE WORLD ELEMENTS HERE-------------------------------------------


    #pg.draw.rect(world,"red",(2120-1,1550-1,2,2))

    
    

    
    temporaryLosBool, losContactCoord = lineOfSight(cameraCoords,screenToWorldCoords(Mouse_Pos))
    if debugMode:
        for i in range(len(allWallEdgesList[0])):
            pg.draw.line(world,"red",allWallEdgesList[0][i],allWallEdgesList[1][i],3)
        if temporaryLosBool==False:
            pg.draw.circle(world,"green",losContactCoord,6)  

    for i in listOfPoints:
        pg.draw.circle(world,"cyan",i,5)
            
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
